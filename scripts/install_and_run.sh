#!/bin/bash
cd "$(dirname "$0")/.."  # Move to root directory
echo "Installation des dependances..."
python3 -m pip install -r requirements.txt

echo
echo "Creation du fichier .env..."
echo "MODBUS_IP_ADDRESS=192.168.0.4" > .env

echo
echo "Execution du programme..."
python3 get_all_values.py

echo
echo "Appuyez sur Entrée pour fermer..."
read 
