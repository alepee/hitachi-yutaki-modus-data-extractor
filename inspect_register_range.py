"""
Interactive tool to inspect specific ranges of Modbus registers
Useful for focused exploration of undocumented registers
"""

import argparse
import sys
from pymodbus.client import ModbusTcpClient
from pymodbus.exceptions import ModbusException
from dotenv import load_dotenv
import os


def read_registers(ip_address, start, end):
    """
    Read a specific range of registers and display them
    
    Args:
        ip_address: IP address of the Modbus device
        start: Starting register address
        end: Ending register address
    """
    client = ModbusTcpClient(ip_address, timeout=3)
    
    try:
        if not client.connect():
            print(f"❌ Failed to connect to {ip_address}")
            return False
        
        print(f"✓ Connected to {ip_address}")
        print(f"\n{'Register':<10} {'Address':<10} {'Decimal':<10} {'Hex':<10} {'Binary':<18} {'ASCII':<10} {'IP Octet':<12} {'Temp °C':<10}")
        print("-" * 100)
        
        for address in range(start, end + 1):
            try:
                result = client.read_holding_registers(address=address, count=1)
                
                if not result.isError() and hasattr(result, 'registers'):
                    value = result.registers[0]
                    register = address + 1
                    
                    # Decimal
                    dec_str = str(value)
                    
                    # Hexadecimal
                    hex_str = f"0x{value:04X}"
                    
                    # Binary
                    bin_str = f"{value:016b}"
                    
                    # ASCII
                    high_byte = (value >> 8) & 0xFF
                    low_byte = value & 0xFF
                    ascii_str = ""
                    if 32 <= high_byte <= 126:
                        ascii_str += chr(high_byte)
                    else:
                        ascii_str += "."
                    if 32 <= low_byte <= 126:
                        ascii_str += chr(low_byte)
                    else:
                        ascii_str += "."
                    
                    # IP octet (if applicable)
                    ip_str = str(value) if value <= 255 else "N/A"
                    
                    # Temperature (signed with decimal)
                    if value > 32767:
                        temp = (value - 65536) / 10
                    else:
                        temp = value / 10
                    temp_str = f"{temp:.1f}"
                    
                    print(f"{register:<10} {address:<10} {dec_str:<10} {hex_str:<10} {bin_str:<18} {ascii_str:<10} {ip_str:<12} {temp_str:<10}")
                else:
                    print(f"{address + 1:<10} {address:<10} {'ERROR':<10}")
                    
            except Exception as e:
                print(f"{address + 1:<10} {address:<10} ERROR: {e}")
        
        print("-" * 100)
        
        # Try to detect patterns
        print("\n🔍 Pattern Detection:")
        print("-" * 50)
        
        # Read all values again for pattern analysis
        all_values = []
        for address in range(start, end + 1):
            try:
                result = client.read_holding_registers(address=address, count=1)
                if not result.isError() and hasattr(result, 'registers'):
                    all_values.append((address, result.registers[0]))
            except:
                pass
        
        # Check for IP pattern
        if len(all_values) >= 4:
            print("\n📡 Checking for IP address patterns (4 consecutive registers with values 0-255):")
            for i in range(len(all_values) - 3):
                values = [all_values[i+j][1] for j in range(4)]
                if all(0 <= v <= 255 for v in values):
                    ip = ".".join(str(v) for v in values)
                    start_reg = all_values[i][0] + 1
                    end_reg = all_values[i+3][0] + 1
                    print(f"  → Registers {start_reg}-{end_reg}: {ip}")
        
        # Check for ASCII strings
        print("\n📝 Checking for ASCII string patterns:")
        current_string = ""
        string_start = None
        for addr, value in all_values:
            high_byte = (value >> 8) & 0xFF
            low_byte = value & 0xFF
            
            chars = ""
            if 32 <= high_byte <= 126:
                chars += chr(high_byte)
            if 32 <= low_byte <= 126:
                chars += chr(low_byte)
            
            if chars:
                if string_start is None:
                    string_start = addr + 1
                current_string += chars
            else:
                if len(current_string) >= 4:
                    print(f"  → Registers {string_start}-{addr}: '{current_string}'")
                current_string = ""
                string_start = None
        
        if len(current_string) >= 4:
            print(f"  → Registers {string_start}-{all_values[-1][0] + 1}: '{current_string}'")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    finally:
        client.close()


def main():
    parser = argparse.ArgumentParser(
        description='Inspect specific ranges of Modbus registers',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Inspect registers 1-50 (addresses 0-49)
  python inspect_register_range.py 0 49
  
  # Inspect around suspected gateway info area
  python inspect_register_range.py 0 100
  
  # Check specific suspicious registers
  python inspect_register_range.py 100 110
  
Note: Register number = Address + 1
      (e.g., Register 1 = Address 0)
        """
    )
    
    parser.add_argument('start', type=int, help='Starting register address (e.g., 0 for register 1)')
    parser.add_argument('end', type=int, help='Ending register address')
    parser.add_argument('--ip', type=str, help='Modbus IP address (overrides .env file)')
    
    args = parser.parse_args()
    
    # Validate range
    if args.start < 0 or args.end < 0:
        print("❌ Error: Address range must be non-negative")
        sys.exit(1)
    
    if args.start > args.end:
        print("❌ Error: Start address must be <= end address")
        sys.exit(1)
    
    if args.end - args.start > 1000:
        print("⚠️  Warning: Large range may take a while...")
        response = input("Continue? (y/n): ")
        if response.lower() != 'y':
            sys.exit(0)
    
    # Load environment
    load_dotenv()
    
    # Get IP address
    modbus_ip = args.ip or os.getenv('MODBUS_IP_ADDRESS')
    if not modbus_ip:
        print("❌ Error: MODBUS_IP_ADDRESS not set in .env file and not provided via --ip")
        sys.exit(1)
    
    print("=" * 100)
    print(f"Inspecting Modbus Registers: {args.start + 1}-{args.end + 1} (Addresses: {args.start}-{args.end})")
    print(f"Target: {modbus_ip}")
    print("=" * 100)
    
    success = read_registers(modbus_ip, args.start, args.end)
    
    if not success:
        sys.exit(1)


if __name__ == "__main__":
    main()
