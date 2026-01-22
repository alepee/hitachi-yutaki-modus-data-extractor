"""
Scan undocumented Modbus registers (addresses 0-999)
Based on suggestion from PCR-2020 to inspect lower registers
that may contain gateway information (IP address, firmware version, etc.)
"""

import csv
import datetime
import os
import time
from pymodbus.client import ModbusTcpClient
from pymodbus.exceptions import ModbusException
from dotenv import load_dotenv


def scan_registers(ip_address, start_address=0, end_address=999, batch_size=10, delay=0.1):
    """
    Scan a range of Modbus registers and return those with valid values
    
    Args:
        ip_address: IP address of the Modbus device
        start_address: Starting register address (default: 0)
        end_address: Ending register address (default: 999)
        batch_size: Number of registers to read at once (default: 10)
        delay: Delay between reads in seconds (default: 0.1)
    
    Returns:
        List of tuples: (register_number, address, raw_value, possible_interpretations)
    """
    client = ModbusTcpClient(ip_address, timeout=3)
    results = []
    
    try:
        if not client.connect():
            raise ConnectionError(f"Failed to connect to {ip_address}")
        
        print(f"Connected to {ip_address}")
        print(f"Scanning registers from {start_address} to {end_address}...")
        
        for address in range(start_address, end_address + 1):
            try:
                # Read single register
                result = client.read_holding_registers(address=address, count=1)
                
                if not result.isError() and hasattr(result, 'registers'):
                    raw_value = result.registers[0]
                    register_number = address + 1  # Register number = address + 1
                    
                    # Generate possible interpretations
                    interpretations = interpret_value(raw_value, address)
                    
                    results.append((register_number, address, raw_value, interpretations))
                    print(f"Register {register_number} (addr {address}): {raw_value} - {interpretations}")
                
                # Small delay to avoid overwhelming the device
                time.sleep(delay)
                
                # Progress indicator
                if (address + 1) % 100 == 0:
                    print(f"Progress: {address + 1}/{end_address + 1} addresses scanned")
                    
            except Exception as e:
                print(f"Error reading address {address}: {e}")
                continue
                
    except Exception as e:
        print(f"Connection error: {e}")
    finally:
        client.close()
        print("Connection closed")
    
    return results


def interpret_value(value, address):
    """
    Provide possible interpretations for a raw register value
    
    Args:
        value: Raw register value (0-65535)
        address: Register address
    
    Returns:
        String with possible interpretations
    """
    interpretations = []
    
    # As decimal
    interpretations.append(f"Dec: {value}")
    
    # As hexadecimal
    interpretations.append(f"Hex: 0x{value:04X}")
    
    # As binary
    interpretations.append(f"Bin: {value:016b}")
    
    # As ASCII characters (high byte, low byte)
    high_byte = (value >> 8) & 0xFF
    low_byte = value & 0xFF
    ascii_str = ""
    if 32 <= high_byte <= 126:  # Printable ASCII range
        ascii_str += chr(high_byte)
    if 32 <= low_byte <= 126:
        ascii_str += chr(low_byte)
    if ascii_str:
        interpretations.append(f"ASCII: '{ascii_str}'")
    
    # As potential IP address octet (if value <= 255)
    if value <= 255:
        interpretations.append(f"IP octet: {value}")
    
    # As temperature (signed, with decimal)
    if value > 32767:  # Handle as signed 16-bit
        signed_value = value - 65536
        interpretations.append(f"Temp: {signed_value/10:.1f}°C")
    else:
        interpretations.append(f"Temp: {value/10:.1f}°C")
    
    return " | ".join(interpretations)


def analyze_ip_patterns(results):
    """
    Look for patterns that could represent IP addresses
    4 consecutive registers with values 0-255
    
    Args:
        results: List of scan results
    
    Returns:
        List of potential IP address locations
    """
    potential_ips = []
    
    for i in range(len(results) - 3):
        values = [results[i+j][2] for j in range(4)]
        
        # Check if all 4 values are valid IP octets (0-255)
        if all(0 <= v <= 255 for v in values):
            ip_address = ".".join(str(v) for v in values)
            start_reg = results[i][0]
            end_reg = results[i+3][0]
            potential_ips.append((start_reg, end_reg, ip_address))
    
    return potential_ips


def analyze_ascii_patterns(results):
    """
    Look for patterns that could represent ASCII strings
    
    Args:
        results: List of scan results
    
    Returns:
        List of potential ASCII string locations
    """
    potential_strings = []
    current_string = ""
    start_reg = None
    
    for reg_num, addr, value, interp in results:
        high_byte = (value >> 8) & 0xFF
        low_byte = value & 0xFF
        
        chars = ""
        if 32 <= high_byte <= 126:
            chars += chr(high_byte)
        if 32 <= low_byte <= 126:
            chars += chr(low_byte)
        
        if chars:
            if start_reg is None:
                start_reg = reg_num
            current_string += chars
        else:
            if len(current_string) >= 4:  # At least 4 characters
                potential_strings.append((start_reg, reg_num - 1, current_string))
            current_string = ""
            start_reg = None
    
    # Check final string
    if len(current_string) >= 4:
        potential_strings.append((start_reg, results[-1][0], current_string))
    
    return potential_strings


def export_results(results, timestamp):
    """
    Export scan results to CSV file
    
    Args:
        results: List of scan results
        timestamp: Timestamp string for filename
    
    Note:
        Files are saved to extracted_data/ by default (gitignored).
        For important discovery results you want to version control,
        manually move the CSV file to the project root.
    """
    os.makedirs('./extracted_data', exist_ok=True)
    filename = f'./extracted_data/undocumented_registers-{timestamp}.csv'
    
    with open(filename, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['register', 'address', 'raw_value', 'interpretations'])
        
        for reg_num, addr, value, interp in results:
            writer.writerow([reg_num, addr, value, interp])
    
    print(f"\nResults exported to: {filename}")
    return filename


def main():
    # Load environment variables
    load_dotenv()
    
    # Get configuration
    modbus_ip = os.getenv('MODBUS_IP_ADDRESS')
    if not modbus_ip:
        raise ValueError("MODBUS_IP_ADDRESS not set in .env file")
    
    # Get current timestamp
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    
    print("=" * 60)
    print("Scanning Undocumented Modbus Registers")
    print("=" * 60)
    print(f"Target: {modbus_ip}")
    print(f"Range: Registers 1-1000 (Addresses 0-999)")
    print("=" * 60)
    print()
    
    # Scan registers
    results = scan_registers(modbus_ip, start_address=0, end_address=999)
    
    print(f"\n\nScan complete! Found {len(results)} registers with valid values.")
    
    # Export results
    csv_file = export_results(results, timestamp)
    
    # Analyze patterns
    print("\n" + "=" * 60)
    print("PATTERN ANALYSIS")
    print("=" * 60)
    
    # Look for IP addresses
    print("\nPotential IP Addresses:")
    print("-" * 60)
    ip_patterns = analyze_ip_patterns(results)
    if ip_patterns:
        for start, end, ip in ip_patterns:
            print(f"  Registers {start}-{end}: {ip}")
    else:
        print("  No obvious IP address patterns found")
    
    # Look for ASCII strings
    print("\nPotential ASCII Strings:")
    print("-" * 60)
    ascii_patterns = analyze_ascii_patterns(results)
    if ascii_patterns:
        for start, end, string in ascii_patterns:
            print(f"  Registers {start}-{end}: '{string}'")
    else:
        print("  No obvious ASCII string patterns found")
    
    # Summary statistics
    print("\n" + "=" * 60)
    print("SUMMARY STATISTICS")
    print("=" * 60)
    print(f"Total registers scanned: 1000 (addresses 0-999)")
    print(f"Registers with values: {len(results)}")
    print(f"Empty/error registers: {1000 - len(results)}")
    
    if results:
        values = [r[2] for r in results]
        print(f"Value range: {min(values)} - {max(values)}")
        non_zero = [v for v in values if v != 0]
        if non_zero:
            print(f"Non-zero values: {len(non_zero)}")
        
        # Registers with small values (likely config/status)
        small_values = [r for r in results if r[2] <= 255]
        print(f"Registers with values ≤ 255: {len(small_values)}")
    
    print("\n" + "=" * 60)
    print(f"Results saved to: {csv_file}")
    print("=" * 60)


if __name__ == "__main__":
    main()
