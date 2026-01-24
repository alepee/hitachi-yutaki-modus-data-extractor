"""
Get unique ID from Hitachi ATW-MBS-02 gateway using Input Registers.

This is the RECOMMENDED method for Home Assistant integration.
It works in Docker containers (no ARP table needed).
"""

import argparse
import os
from typing import Optional, Dict, List
from pymodbus.client import ModbusTcpClient
from dotenv import load_dotenv


# Unit model mapping (register 1219)
UNIT_MODELS = {
    0: "YUTAKI S",
    1: "YUTAKI S COMBI",
    2: "S80",
    3: "M"
}

# System configuration bits (register 1090)
SYSTEM_CONFIG_BITS = {
    0: "Circuit 1 Heating",
    1: "Circuit 2 Heating",
    2: "Circuit 1 Cooling",
    3: "Circuit 2 Cooling",
    4: "DHWT",
    5: "SWP",
    6: "Room thermostat Circuit 1",
    7: "Room thermostat Circuit 2",
    8: "Wireless setting Circuit 1",
    9: "Wireless setting Circuit 2",
    10: "Wireless room temperature Circuit 1",
    11: "Wireless room temperature Circuit 2"
}


def get_gateway_unique_id(ip_address: str, timeout: int = 3) -> Optional[str]:
    """
    Read unique ID from gateway's Input Registers.
    
    The ATW-MBS-02 gateway exposes a stable identifier in Input Registers 1-3
    (addresses 0-2). This ID is persistent and suitable for Home Assistant's
    unique_id requirements.
    
    Args:
        ip_address: Gateway IP address
        timeout: Connection timeout in seconds
    
    Returns:
        Unique ID string (format: "3846-103-56") or None if failed
    """
    client = ModbusTcpClient(ip_address, timeout=timeout)
    
    try:
        if not client.connect():
            print(f"❌ Failed to connect to {ip_address}")
            return None
        
        # Read Input Registers at addresses 0-2 (function code 04)
        result = client.read_input_registers(address=0, count=3)
        
        if result.isError() or not hasattr(result, 'registers'):
            print(f"❌ Failed to read Input Registers from {ip_address}")
            return None
        
        values = result.registers
        
        # Format as decimal string: "3846-103-56"
        unique_id = '-'.join(str(v) for v in values)
        
        return unique_id
        
    except Exception as e:
        print(f"❌ Error reading unique ID: {e}")
        return None
    finally:
        client.close()


def get_gateway_unique_id_hex(ip_address: str, timeout: int = 3) -> Optional[str]:
    """
    Read unique ID and format as hexadecimal string (MAC-style).
    
    Args:
        ip_address: Gateway IP address
        timeout: Connection timeout in seconds
    
    Returns:
        Unique ID string (format: "0F06:0067:0038") or None if failed
    """
    client = ModbusTcpClient(ip_address, timeout=timeout)
    
    try:
        if not client.connect():
            return None
        
        result = client.read_input_registers(address=0, count=3)
        
        if result.isError() or not hasattr(result, 'registers'):
            return None
        
        values = result.registers
        
        # Format as hex string: "0F06:0067:0038"
        unique_id = ':'.join(f'{v:04X}' for v in values)
        
        return unique_id
        
    except Exception:
        return None
    finally:
        client.close()


def verify_unique_id_available(ip_address: str) -> bool:
    """
    Verify that the gateway supports unique ID reading.
    
    Args:
        ip_address: Gateway IP address
    
    Returns:
        True if unique ID can be read, False otherwise
    """
    unique_id = get_gateway_unique_id(ip_address)
    return unique_id is not None


def get_unit_model(ip_address: str, timeout: int = 3) -> Optional[str]:
    """
    Read unit model from Holding Register 1219.
    
    Args:
        ip_address: Gateway IP address
        timeout: Connection timeout in seconds
    
    Returns:
        Unit model name or None if failed
    """
    client = ModbusTcpClient(ip_address, timeout=timeout)
    
    try:
        if not client.connect():
            return None
        
        # Read Holding Register 1219 (address 1218, function code 03)
        result = client.read_holding_registers(address=1218, count=1)
        
        if result.isError() or not hasattr(result, 'registers'):
            return None
        
        model_code = result.registers[0]
        return UNIT_MODELS.get(model_code, f"Unknown ({model_code})")
        
    except Exception:
        return None
    finally:
        client.close()


def get_system_configuration(ip_address: str, timeout: int = 3) -> Optional[Dict[str, bool]]:
    """
    Read system configuration from Holding Register 1090.
    
    Returns a dictionary with configuration features and their status.
    
    Args:
        ip_address: Gateway IP address
        timeout: Connection timeout in seconds
    
    Returns:
        Dictionary with feature names and boolean values, or None if failed
    """
    client = ModbusTcpClient(ip_address, timeout=timeout)
    
    try:
        if not client.connect():
            return None
        
        # Read Holding Register 1090 (address 1089, function code 03)
        result = client.read_holding_registers(address=1089, count=1)
        
        if result.isError() or not hasattr(result, 'registers'):
            return None
        
        config_value = result.registers[0]
        
        # Parse bits
        config = {}
        for bit_num, feature_name in SYSTEM_CONFIG_BITS.items():
            config[feature_name] = bool(config_value & (1 << bit_num))
        
        return config
        
    except Exception:
        return None
    finally:
        client.close()


def format_system_configuration(config: Dict[str, bool]) -> List[str]:
    """
    Format system configuration as a list of enabled features.
    
    Args:
        config: Dictionary with feature names and boolean values
    
    Returns:
        List of enabled feature names
    """
    return [feature for feature, enabled in config.items() if enabled]


def main():
    """Demo: Read and display gateway unique ID."""
    parser = argparse.ArgumentParser(
        description='Get unique ID from Hitachi ATW-MBS-02 gateway'
    )
    parser.add_argument(
        '--ip',
        type=str,
        help='Gateway IP address (overrides .env file)'
    )
    
    args = parser.parse_args()
    
    # Get IP from command line or .env file
    modbus_ip = args.ip
    
    if not modbus_ip:
        load_dotenv()
        modbus_ip = os.getenv('MODBUS_IP_ADDRESS')
    
    if not modbus_ip:
        print("❌ Error: No IP address provided")
        print()
        print("Usage:")
        print("  python get_gateway_unique_id.py --ip 192.168.0.4")
        print()
        print("Or create a .env file with:")
        print("  MODBUS_IP_ADDRESS=192.168.0.4")
        return
    
    print("=" * 70)
    print("Gateway Unique ID Retrieval")
    print("=" * 70)
    print(f"Target: {modbus_ip}")
    print()
    
    # Get unique ID (decimal format)
    unique_id = get_gateway_unique_id(modbus_ip)
    
    if unique_id:
        print(f"✅ Unique ID (decimal): {unique_id}")
        
        # Also show hex format
        unique_id_hex = get_gateway_unique_id_hex(modbus_ip)
        if unique_id_hex:
            print(f"✅ Unique ID (hex):     {unique_id_hex}")
        
        print()
        
        # Get unit model
        model = get_unit_model(modbus_ip)
        if model:
            print(f"📦 Unit Model:          {model}")
        else:
            print("⚠️  Unit Model:          Unable to read")
        
        # Get system configuration
        config = get_system_configuration(modbus_ip)
        if config:
            enabled_features = format_system_configuration(config)
            print(f"⚙️  Configuration:       {len(enabled_features)} features enabled")
            print()
            print("Enabled features:")
            for feature in enabled_features:
                print(f"  ✓ {feature}")
        else:
            print("⚠️  Configuration:       Unable to read")
        
    else:
        print(f"❌ Failed to retrieve unique ID from {modbus_ip}")
        print()
        print("Troubleshooting:")
        print("  1. Verify gateway is reachable")
        print("  2. Check IP address")
        print("  3. Ensure Modbus TCP is enabled on gateway")
    
    print()
    print("=" * 70)


if __name__ == "__main__":
    main()
