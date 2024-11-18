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

## Support

If you need additional help:

1. Verify that all prerequisites are met
2. Ensure the gateway is accessible on the network
3. Check physical connections between the heat pump and gateway 
