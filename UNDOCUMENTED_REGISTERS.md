# Undocumented Registers Discovery

This document summarizes the findings from scanning undocumented Modbus registers (addresses 0-999) on the Hitachi ATW-MBS-02 gateway.

## Scan Date

2026-01-22 02:02:24

## Key Discoveries

### Network Configuration Registers

The gateway stores its complete network configuration in registers 21-33:

| Register | Address | Value | Description |
|----------|---------|-------|-------------|
| 21 | 20 | 192 | Gateway IP - Octet 1 |
| 22 | 21 | 168 | Gateway IP - Octet 2 |
| 23 | 22 | 0 | Gateway IP - Octet 3 |
| 24 | 23 | 4 | Gateway IP - Octet 4 |
| 25 | 24 | 502 | Modbus TCP Port |
| 26 | 25 | 255 | Subnet Mask - Octet 1 |
| 27 | 26 | 255 | Subnet Mask - Octet 2 |
| 28 | 27 | 255 | Subnet Mask - Octet 3 |
| 29 | 28 | 0 | Subnet Mask - Octet 4 |
| 30 | 29 | 192 | Default Gateway - Octet 1 |
| 31 | 30 | 168 | Default Gateway - Octet 2 |
| 32 | 31 | 0 | Default Gateway - Octet 3 |
| 33 | 32 | 1 | Default Gateway - Octet 4 |

**Gateway IP**: 192.168.0.4  
**Subnet Mask**: 255.255.255.0  
**Default Gateway**: 192.168.0.1  
**Modbus Port**: 502

### Other Notable Registers

| Register | Address | Value | Description/Notes |
|----------|---------|-------|-------------------|
| 1 | 0 | 3846 | Unknown - Could be device type or model |
| 2-3 | 1-2 | 103, 56 | ASCII 'g8' - Possible gateway identifier |
| 7 | 6 | 2 | Unknown configuration value |
| 13 | 12 | 5 | Unknown configuration value |
| 16 | 15 | 1 | Boolean flag or counter |
| 35 | 34 | 10 | Unknown configuration value |
| 41-44 | 40-43 | 13484, 13481, 13485, 13486 | ASCII '4444' - Possible version or identifier |
| 51-58 | 50-57 | See below | Additional IP address references |

### Additional Network References

Registers 51-58 contain what appear to be IP addresses in 16-bit word format:

- Registers 51-52: 0xC0A8 0x00D2 = 192.168.0.210
- Registers 53-54: 0xC0A8 0x00D2 = 192.168.0.210 (duplicate)
- Registers 55-56: 0xC0A8 0x00D7 = 192.168.0.215
- Registers 57-58: 0xC0A8 0x00D7 = 192.168.0.215 (duplicate)

These could be:
- DHCP client addresses
- Previously connected devices
- DNS server addresses
- Reserved addresses

### Special Value Patterns

- **0xFFFF (65535)**: Many registers (81-200+) contain this value, indicating uninitialized or disabled features
- **0x0000 (0)**: Many registers contain zero, indicating disabled features or default values
- **254 (0xFE)**: Registers 75-80 all contain 254, possibly a special marker

## Statistics

- **Total registers scanned**: 1000 (addresses 0-999)
- **Registers with values**: 1000 (100%)
- **Non-zero values**: 963 (96.3%)
- **Registers with values ≤ 255**: 69 (6.9%)
- **Value range**: 0 - 65535

## Use Cases

### Reading Gateway Configuration

To read the gateway's IP address programmatically:

```python
from pymodbus.client import ModbusTcpClient

client = ModbusTcpClient('192.168.0.4')
client.connect()

# Read IP address (4 registers starting at address 20)
result = client.read_holding_registers(address=20, count=4)
if not result.isError():
    ip_address = ".".join(str(v) for v in result.registers)
    print(f"Gateway IP: {ip_address}")

# Read subnet mask (4 registers starting at address 25)
result = client.read_holding_registers(address=25, count=4)
if not result.isError():
    subnet_mask = ".".join(str(v) for v in result.registers)
    print(f"Subnet Mask: {subnet_mask}")

# Read default gateway (4 registers starting at address 29)
result = client.read_holding_registers(address=29, count=4)
if not result.isError():
    default_gw = ".".join(str(v) for v in result.registers)
    print(f"Default Gateway: {default_gw}")

client.close()
```

### Integration with Home Assistant

These registers could be added to the [hass-hitachi_yutaki](https://github.com/alepee/hass-hitachi_yutaki) integration as diagnostic sensors:

- Gateway IP address (read-only)
- Gateway subnet mask (read-only)
- Gateway default gateway (read-only)
- Modbus port (read-only)
- Connected devices count (if identifiable)

## Credits

Discovery based on suggestion by [@PCR-2020](https://github.com/PCR-2020) in [discussion #144](https://github.com/alepee/hass-hitachi_yutaki/discussions/144).

## Further Research Needed

- **Registers 1-20**: Purpose unclear, may contain device identifiers or firmware info
- **Registers 51-58**: Network addresses - purpose unclear (DHCP? DNS? Historical?)
- **Registers 41-44**: ASCII '4444' - version number or identifier?
- **Registers 200+**: Large range of 0xFFFF values - what activates these?
- **Write access**: Are any of these registers writable? (Could allow IP configuration via Modbus)

## Raw Data

Full scan results available in:
```
undocumented_registers-20260122_020224.csv
```

This file is stored at the project root (not in `extracted_data/`) to ensure it's versioned in Git for reference.

## Tools Used

- `scan_undocumented_registers.py` - Full register scanner
- `inspect_register_range.py` - Targeted register inspector

Both tools available in this repository.
