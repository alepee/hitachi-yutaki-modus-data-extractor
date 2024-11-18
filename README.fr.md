# Lecteur de données Hitachi Yutaki via Modbus

Ce programme permet de lire les données de votre Pompe à Chaleur Hitachi Yutaki via la passerelle Modbus ATW-MBS-02. Il génère automatiquement des rapports au format CSV et PDF.

## Compatibilité

Compatible avec les modèles Hitachi Yutaki suivants :

- Yutaki S
- Yutaki S Combi
- Yutaki S80
- Yutaki M

## Prérequis

- Python 3.7 ou plus récent
- Une passerelle ATW-MBS-02 connectée à votre PAC
- Le fichier modbus.csv (fourni avec le programme)
- Une connexion réseau vers la passerelle ATW-MBS-02

## Installation et utilisation

### Pour Windows

1. Téléchargez et installez Python depuis [python.org](https://www.python.org/downloads/)
   - Lors de l'installation, **cochez la case "Add Python to PATH"**
2. Double-cliquez sur `scripts/install_and_run.bat`

### Pour Linux/Mac

1. Ouvrez un terminal
2. Rendez le script exécutable avec la commande :

    ```sh
    chmod +x scripts/install_and_run.sh
    ```

3. Exécutez le script :

    ```sh
    ./scripts/install_and_run.sh
    ```

## Configuration de la passerelle

1. Vérifiez que votre passerelle ATW-MBS-02 est correctement connectée :
   - À votre PAC Hitachi via le port H-LINK
   - À votre réseau local via le port Ethernet

2. Notez l'adresse IP de votre passerelle ATW-MBS-02 :
   - Par défaut : 192.168.0.4
   - Si vous avez changé l'IP, utilisez la nouvelle adresse

3. Configurez l'adresse IP dans le programme :
   - Ouvrez le fichier `.env` avec un éditeur de texte
   - Modifiez l'adresse IP après `MODBUS_IP_ADDRESS=`
   - Sauvegardez le fichier

## Résultats

Les fichiers générés se trouvent dans le dossier `extracted_data` :

- Un fichier CSV contenant toutes les valeurs brutes
- Un fichier PDF avec un rapport détaillé et interprété, incluant :
  - États de fonctionnement
  - Températures
  - Modes de fonctionnement
  - Alarmes éventuelles
  - Configurations actives

Les fichiers sont horodatés pour garder un historique des lectures.

## Dépannage

Si vous rencontrez des problèmes :

1. Vérification de Python :
   - Ouvrez une invite de commande
   - Tapez `python --version`
   - Vous devriez voir la version de Python (3.7 ou plus)

2. Vérification de la connexion à la passerelle :
   - Ouvrez une invite de commande
   - Tapez `ping` suivi de l'adresse IP de votre passerelle
   - Exemple : `ping 192.168.0.4`
   - Vous devriez recevoir des réponses

3. Vérifications des fichiers :
   - Le fichier modbus.csv doit être présent
   - Le fichier .env doit contenir la bonne adresse IP
   - Les droits d'écriture dans le dossier doivent être corrects

4. Messages d'erreur courants :
   - "ModbusException" : Problème de connexion à la passerelle
   - "FileNotFoundError" : Fichier modbus.csv manquant
   - "Permission denied" : Problème de droits d'accès

## Support

Si vous avez besoin d'aide supplémentaire :

1. Vérifiez que tous les prérequis sont remplis
2. Assurez-vous que la passerelle est accessible sur le réseau
3. Vérifiez les connexions physiques entre la PAC et la passerelle
