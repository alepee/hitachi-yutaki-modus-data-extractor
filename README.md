# Hitachi Yutaki Modbus Data Reader

🇫🇷 French version of this document [is available in README.fr.md](https://github.com/alepee/hitachi-yutaki-modus-data-extractor/blob/main/README.fr.md)

This program reads data from your Hitachi Yutaki Heat Pump via the ATW-MBS-02 Modbus gateway. It automatically generates CSV and PDF reports.

## Compatibility

Compatible with the following Hitachi Yutaki models:

- Yutaki S
- Yutaki S Combi
- Yutaki S80
- Yutaki M

## Prerequisites

- Python 3.7 or newer
- An ATW-MBS-02 gateway connected to your heat pump
- The modbus.csv file (provided with the program)
- Network connection to the ATW-MBS-02 gateway

## Installation and Usage

### For Windows

1. Download and install Python from [python.org](https://www.python.org/downloads/)
   - During installation, **check the "Add Python to PATH" box**
2. Double-click on `scripts/install_and_run.bat`

### For Linux/Mac

1. Open a terminal
2. Make the script executable with the command:

    ```sh
    chmod +x scripts/install_and_run.sh
    ```

3. Run the script:

    ```sh
    ./scripts/install_and_run.sh
    ```

## Gateway Configuration

1. Verify that your ATW-MBS-02 gateway is properly connected:
   - To your Hitachi heat pump via the H-LINK port
   - To your local network via the Ethernet port

2. Note the IP address of your ATW-MBS-02 gateway:
   - Default: 192.168.0.4
   - If you changed the IP, use the new address

3. Configure the IP address in the program:
   - Open the `.env` file with a text editor
   - Modify the IP address after `MODBUS_IP_ADDRESS=`
   - Save the file

## Results

Generated files are stored in the `extracted_data` folder:

- A CSV file containing all raw values
- A PDF file with a detailed interpreted report, including:
  - Operating states
  - Temperatures
  - Operating modes
  - Potential alarms
  - Active configurations

Files are timestamped to maintain a reading history.

## Troubleshooting

If you encounter problems:

1. Python verification:
   - Open a command prompt
   - Type `python --version`
   - You should see the Python version (3.7 or higher)

2. Gateway connection verification:
   - Open a command prompt
   - Type `ping` followed by your gateway's IP address
   - Example: `ping 192.168.0.4`
   - You should receive responses

3. File checks:
   - The modbus.csv file must be present
   - The .env file must contain the correct IP address
   - Write permissions in the folder must be correct

4. Common error messages:
   - "ModbusException": Gateway connection problem
   - "FileNotFoundError": Missing modbus.csv file
   - "Permission denied": Access rights problem

## Gateway Unique ID (Home Assistant)

This project includes a tool to retrieve your gateway's unique identifier, needed for the [Home Assistant integration](https://github.com/alepee/hass-hitachi_yutaki) (see [issue #162](https://github.com/alepee/hass-hitachi_yutaki/issues/162)).

### Quick Start

```sh
# Linux/macOS
./scripts/get_unique_id.sh

# Windows
scripts\get_unique_id.bat
```

The script will prompt for your gateway IP and display:
```
✅ Unique ID (decimal): 3846-103-56
✅ Unique ID (hex):     0F06:0067:0038
📦 Unit Model:          S80
```

**Help us validate this feature** by sharing your unique ID on [issue #162](https://github.com/alepee/hass-hitachi_yutaki/issues/162).

For technical details, see [docs/UNIQUE_ID_SOLUTION.md](docs/UNIQUE_ID_SOLUTION.md).

## Advanced Tools: Exploring Undocumented Registers

In addition to reading documented registers, this project includes tools to explore undocumented Modbus registers (addresses 0-999). These registers may contain additional information about the gateway itself, such as IP address, firmware version, and other system data.

### Full Scan of Undocumented Registers

To scan all undocumented registers (0-999):

```sh
python scan_undocumented_registers.py
```

This will:
- Read all registers from address 0 to 999
- Save results to a CSV file in `extracted_data/` (gitignored)
- Automatically detect potential patterns:
  - IP addresses (4 consecutive registers with values 0-255)
  - ASCII strings (readable text embedded in registers)
  - Statistical analysis of found values

**⚠️ Warning:** This scan reads 1000 registers and may take several minutes to complete.

**💾 Note:** Results are saved to `extracted_data/` by default (not version controlled). If you want to keep important discovery results in Git, manually move the generated CSV file to the project root (see `undocumented_registers-20260122_020224.csv` as an example).

### Targeted Register Inspection

To inspect a specific range of registers:

```sh
python inspect_register_range.py <start_address> <end_address>
```

Examples:

```sh
# Inspect the first 50 registers (addresses 0-49, registers 1-50)
python inspect_register_range.py 0 49

# Inspect a specific suspicious area
python inspect_register_range.py 100 150

# Use a custom IP address
python inspect_register_range.py 0 49 --ip 192.168.1.100
```

This tool displays:
- Decimal, hexadecimal, and binary representations
- ASCII interpretation (if printable characters)
- Potential IP octet values
- Temperature interpretation (signed value with decimal)
- Automatic pattern detection (IP addresses, ASCII strings)

### Use Cases

Based on community feedback (see [discussion #144](https://github.com/alepee/hass-hitachi_yutaki/discussions/144)), these tools can help discover:

- **Gateway IP address**: Likely stored across 4 consecutive registers
- **Gateway firmware version**: May complement registers 1096-1097 (unit and controller firmware)
- **Additional system information**: Undocumented configuration and status data

## Support

If you need additional help:

1. Verify that all prerequisites are met
2. Ensure the gateway is accessible on the network
3. Check physical connections between the heat pump and gateway 
