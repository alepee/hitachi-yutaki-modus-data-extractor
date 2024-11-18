@echo off
echo Installation des dependances...
python -m pip install -r requirements.txt

echo.
echo Creation du fichier .env...
echo MODBUS_IP_ADDRESS=192.168.0.4 > .env

echo.
echo Execution du programme...
python get_all_values.py

echo.
echo Appuyez sur une touche pour fermer...
pause 
