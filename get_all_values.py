import csv
import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from pymodbus.client import ModbusTcpClient
from pymodbus.exceptions import ModbusException
import os
from dotenv import load_dotenv

# Get current timestamp
current_timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

# Load environment variables from .env file
load_dotenv()

# Read addresses from the CSV file
with open('modbus.csv', 'r') as input_file:
    csv_reader = csv.reader(input_file)
    headers = next(csv_reader)  # Read the header row
    addresses = [row[headers.index('address')] for row in csv_reader]

def get_modbus_values(ip_address, addresses):
    client = ModbusTcpClient(ip_address)
    values = []
    try:
        client.connect()
        for address in addresses:
            result = client.read_holding_registers(int(address), 1)
            if not result.isError():
                values.append(str(result.registers[0]))
            else:
                values.append("Error")
    except ModbusException as e:
        print(f"Modbus error: {e}")
    finally:
        client.close()
    return values

# Get the IP address from .env
modbus_ip = os.getenv('MODBUS_IP_ADDRESS')
if not modbus_ip:
    raise ValueError("MODBUS_IP_ADDRESS not set")

# Get modbus values
values = get_modbus_values(modbus_ip, addresses)

# Create a new CSV file with timestamp in the name
# Ensure the extracted_data directory exists
os.makedirs('./extracted_data', exist_ok=True)

output_filename = f'./extracted_data/modbus-{current_timestamp}.csv'
with open(output_filename, 'w', newline='') as output_file:
    csv_writer = csv.writer(output_file)
    
    # Write headers to the new CSV, adding a new column for modbus command output
    csv_writer.writerow(headers + ['value'])
    
    # Open the original CSV file again to read all rows
    with open('modbus.csv', 'r') as input_file:
        csv_reader = csv.reader(input_file)
        next(csv_reader)  # Skip the header row
        
        # Write each row with its corresponding value
        for row, value in zip(csv_reader, values):
            csv_writer.writerow(row + [value])

print(f"Process completed. New file created: {output_filename}")

# Register information dictionary
registers_info = {
    "1001": {
        "name": "Control Unit Run/Stop",
        "values": {0: "Stop", 1: "Run"}
    },
    "1002": {
        "name": "Control Unit Mode",
        "values": {0: "Cool", 1: "Heat", 2: "Auto"}
    },
    "1003": {
        "name": "Control Circuit 1 Run/Stop",
        "values": {0: "Stop", 1: "Run"}
    },
    "1004": {
        "name": "Control Heat. OTC Circuit 1",
        "values": {0: "No", 1: "Points", 2: "Gradient", 3: "Fix"}
    },
    "1005": {
        "name": "Control Cool. OTC Circuit 1",
        "values": {0: "No", 1: "Points", 2: "Fix"}
    },
    "1008": {
        "name": "Control Circuit 1: Eco mode",
        "values": {0: "ECO", 1: "Comfort"}
    },
    "1011": {
        "name": "Control Circuit 1: Thermostat Available",
        "values": {0: "Not Available", 1: "Available"}
    },
    "1014": {
        "name": "Control Circuit 2 Run/Stop",
        "values": {0: "Stop", 1: "Run"}
    },
    "1015": {
        "name": "Control Heat. OTC Circuit 2",
        "values": {0: "No", 1: "Points", 2: "Gradient", 3: "Fix"}
    },
    "1016": {
        "name": "Control Cool. OTC Circuit 2",
        "values": {0: "No", 1: "Points", 2: "Fix"}
    },
    "1019": {
        "name": "Control Circuit 2: Eco mode",
        "values": {0: "ECO", 1: "Comfort"}
    },
    "1022": {
        "name": "Control Circuit 2: Thermostat Available",
        "values": {0: "Not Available", 1: "Available"}
    },
    "1025": {
        "name": "Control DHWT Run/Stop",
        "values": {0: "Stop", 1: "Run"}
    },
    "1027": {
        "name": "Control DHW Boost",
        "values": {0: "No request", 1: "Request"}
    },
    "1028": {
        "name": "Control DHW Demand Mode",
        "values": {0: "Standard", 1: "High demand"}
    },
    "1029": {
        "name": "Control Swimming Pool Run/Stop",
        "values": {0: "Stop", 1: "Run"}
    },
    "1031": {
        "name": "Control Anti Legionella Run",
        "values": {0: "Stop", 1: "Run"}
    },
    "1033": {
        "name": "Control Block menu 6",
        "values": {0: "No", 1: "Block"}
    },
    "1034": {
        "name": "Control BMS Alarm",
        "values": {0: "No Alarm", 1: "Alarm"}
    },
    "1051": {
        "name": "Status Unit Run/Stop",
        "values": {0: "Stop", 1: "Run"}
    },
    "1052": {
        "name": "Status Unit Mode",
        "values": {0: "Cool", 1: "Heat"}
    },
    "1053": {
        "name": "Status Circuit 1 Run/Stop",
        "values": {0: "Stop", 1: "Run"}
    },
    "1054": {
        "name": "Status Heat. OTC Circuit 1",
        "values": {0: "No", 1: "Points", 2: "Gradient", 3: "Fix"}
    },
    "1055": {
        "name": "Status Cool. OTC Circuit 1",
        "values": {0: "No", 1: "Points", 2: "Fix"}
    },
    "1058": {
        "name": "Status Circuit 1: Eco mode",
        "values": {0: "ECO", 1: "Comfort"}
    },
    "1065": {
        "name": "Status Circuit 2 Run/Stop",
        "values": {0: "Stop", 1: "Run"}
    },
    "1066": {
        "name": "Status Heat. OTC Circuit 2",
        "values": {0: "No", 1: "Points", 2: "Gradient", 3: "Fix"}
    },
    "1067": {
        "name": "Status Cool. OTC Circuit 2",
        "values": {0: "No", 1: "Points", 2: "Fix"}
    },
    "1070": {
        "name": "Status Circuit 2: Eco mode",
        "values": {0: "ECO", 1: "Comfort"}
    },
    "1077": {
        "name": "Status DHWT Run/Stop",
        "values": {0: "Stop", 1: "Run"}
    },
    "1079": {
        "name": "Control DHW Boost",
        "values": {0: "Disable", 1: "Enable"}
    },
    "1080": {
        "name": "Status DHW Demand Mode",
        "values": {0: "Standard", 1: "High demand"}
    },
    "1082": {
        "name": "Status Swimming Pool Run/Stop",
        "values": {0: "Stop", 1: "Run"}
    },
    "1085": {
        "name": "Status Anti Legionella Run",
        "values": {0: "Stop", 1: "Run"}
    },
    "1087": {
        "name": "Status Block menu 6",
        "values": {0: "No", 1: "Block"}
    },
    "1088": {
        "name": "Status BMS Alarm",
        "values": {0: "No", 1: "Alarm"}
    },
    "1089": {
        "name": "Central Mode",
        "values": {0: "Local", 1: "Air", 2: "Water", 3: "Full"}
    },
    "1090": {
        "name": "System Configuration",
        "bits": {
            "Circuit 1 Heating": "Bit 0",
            "Circuit 2 Heating": "Bit 1",
            "Circuit 1 Cooling": "Bit 2",
            "Circuit 2 Cooling": "Bit 3",
            "DHWT": "Bit 4",
            "SWP": "Bit 5",
            "Room thermostat Circuit 1": "Bit 6",
            "Room thermostat Circuit 2": "Bit 7",
            "Wireless setting Circuit 1": "Bit 8",
            "Wireless setting Circuit 2": "Bit 9",
            "Wireless room temperature Circuit 1": "Bit 10",
            "Wireless room temperature Circuit 2": "Bit 11"
        }
    },
    "1091": {
        "name": "Operation State",
        "values": {
            0: "OFF",
            1: "Cool Demand-OFF",
            2: "Cool Thermo-OFF",
            3: "Cool Thermo-ON",
            4: "Heat Demand-OFF",
            5: "Heat Thermo-OFF",
            6: "Heat Thermo-ON",
            7: "DHW-OFF",
            8: "DHW-ON",
            9: "SWP-OFF",
            10: "SWP-ON",
            11: "Alarm"
        }
    },
    "1095": {
        "name": "H-LINK communication state",
        "values": {
            0: "No alarm",
            1: "There is no communication with RCS or YUTAKI unit during more than 180 seconds",
            2: "Data initialization"
        }
    },
    "1219": {
        "name": "Unit model",
        "values": {0: "YUTAKI S", 1: "YUTAKI S COMBI", 2: "S80", 3: "M"}
    },
    "1223": {
        "name": "System status",
        "bits": {
            "Defrost": "Bit 0",
            "Solar": "Bit 1",
            "Water Pump 1": "Bit 2",
            "Water Pump 2": "Bit 3",
            "Water Pump 3": "Bit 4",
            "Compressor ON": "Bit 5",
            "Boiler ON": "Bit 6",
            "DHW Heater": "Bit 7",
            "Space Heater": "Bit 8",
            "Smart function input enable": "Bit 9"
        }
    },
    "1224": {
        "name": "Alarm number",
        "special": "alarm"
    }
}

def interpret_bitwise_register(value, register_info):
    try:
        int_value = int(value)
        if "bits" in register_info:
            binary = format(int_value, f'0{len(register_info["bits"])}b')[::-1]
            interpretations = [f"{bit_name}: {'<strong>True</strong>' if binary[i] == '1' else 'False'}" 
                               for i, (bit_name, _) in enumerate(register_info["bits"].items())]
            return "<br/>".join(interpretations)
        elif "values" in register_info:
            return f"{value}: {register_info['values'].get(int_value, 'Unknown state')}"
        elif register_info.get("special") == "alarm":
            return "No Alarm" if int_value == 0 else f"Alarm number: {int_value}"
    except ValueError:
        return value  # Return original value if it's not a valid integer

def interpret_register(register, value, range_info):
    if register in registers_info:
        return interpret_bitwise_register(value, registers_info[register])
    elif ",0 m3/h" in range_info:
        try:
            return f"{float(value)/10:.1f} m3/h"
        except ValueError:
            return value
    elif ",0 °C" in range_info:
        try:
            return f"{float(value)/10:.1f} °C"
        except ValueError:
            return value
    elif "°C" in range_info:
        try:
            return f"{value} °C"
        except ValueError:
            return value
    elif "%" in range_info:
        try:
            return f"{value} %"
        except ValueError:
            return value
    elif "kWh" in range_info:
        try:
            return f"{value} kWh"
        except ValueError:
            return value
    elif "Hz" in range_info:
        try:
            return f"{value} Hz"
        except ValueError:
            return value
    else:
        return value  # Default to original value if no special interpretation

def export_to_pdf(csv_filename, pdf_filename, headers):
    with open(csv_filename, 'r') as csv_file:
        csv_reader = csv.reader(csv_file)
        data = list(csv_reader)

    page_size = landscape(A4)
    doc = SimpleDocTemplate(pdf_filename, pagesize=page_size,
                            leftMargin=10, rightMargin=10,
                            topMargin=10, bottomMargin=10)

    style_header = ParagraphStyle('Header', fontSize=7, leading=8, alignment=TA_CENTER, fontName='Helvetica-Bold')
    style_normal = ParagraphStyle('Normal', fontSize=6, leading=7, fontName='Helvetica')
    style_interpretation = ParagraphStyle('Interpretation', fontSize=6, leading=7, fontName='Helvetica')
    style_interpretation.allowWidows = 0
    style_interpretation.allowOrphans = 0

    # Set headers
    data[0] = ["register","address","description and notice","access","value","interpretation"]
    data[0] = [Paragraph(cell, style_header) for cell in data[0]]

    for key, row in enumerate(data[1:]):
        register_number = row[0]
        address = row[1]
        access = row[4]
        value = row[5]
        description_and_notice = f"<strong>{row[2]}</strong><br/>{"<br/>".join(row[3].split(';'))}"
        interpretation = interpret_register(register_number, value, description_and_notice)

        data[key+1] = [Paragraph(cell, style_normal) for cell in [register_number, address, description_and_notice, access, value, interpretation]]

    available_width = page_size[0]
    width_ratios = [0.05, 0.05, 0.4, 0.05, 0.05, 0.3]
    col_widths = [w * available_width for w in width_ratios]

    table = Table(data, colWidths=col_widths, repeatRows=1)
    
    style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 7),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 5),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 6),
        ('TOPPADDING', (0, 1), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 3),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('ALIGN', (3, 1), (3, -1), 'LEFT'),
        ('ALIGN', (-1, 1), (-1, -1), 'LEFT'),
    ])
    table.setStyle(style)
    
    doc.build([table])

# Export the data to PDF
pdf_filename = f'./extracted_data/modbus-{current_timestamp}.pdf'
export_to_pdf(output_filename, pdf_filename, headers)
print(f"PDF exported: {pdf_filename}")
