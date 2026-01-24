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

## Identifiant unique de la passerelle (Home Assistant)

Ce projet inclut un outil pour récupérer l'identifiant unique de votre passerelle, nécessaire pour l'[intégration Home Assistant](https://github.com/alepee/hass-hitachi_yutaki) (voir [issue #162](https://github.com/alepee/hass-hitachi_yutaki/issues/162)).

### Utilisation rapide

```sh
# Linux/macOS
./scripts/get_unique_id.sh

# Windows
scripts\get_unique_id.bat
```

Le script demandera l'IP de votre passerelle et affichera :
```
✅ Unique ID (decimal): 3846-103-56
✅ Unique ID (hex):     0F06:0067:0038
📦 Unit Model:          S80
```

**Aidez-nous à valider cette fonctionnalité** en partageant votre identifiant unique sur l'[issue #162](https://github.com/alepee/hass-hitachi_yutaki/issues/162).

Pour les détails techniques, voir [docs/UNIQUE_ID_SOLUTION.md](docs/UNIQUE_ID_SOLUTION.md).

## Outils avancés : Explorer les registres non documentés

En plus de la lecture des registres documentés, ce projet inclut des outils pour explorer les registres Modbus non documentés (adresses 0-999). Ces registres peuvent contenir des informations supplémentaires sur la passerelle elle-même, telles que l'adresse IP, la version du firmware et d'autres données système.

### Scan complet des registres non documentés

Pour scanner tous les registres non documentés (0-999) :

```sh
python scan_undocumented_registers.py
```

Cela va :
- Lire tous les registres de l'adresse 0 à 999
- Sauvegarder les résultats dans un fichier CSV dans `extracted_data/` (ignoré par Git)
- Détecter automatiquement les motifs potentiels :
  - Adresses IP (4 registres consécutifs avec des valeurs 0-255)
  - Chaînes ASCII (texte lisible intégré dans les registres)
  - Analyse statistique des valeurs trouvées

**⚠️ Attention :** Ce scan lit 1000 registres et peut prendre plusieurs minutes.

**💾 Note :** Les résultats sont sauvegardés dans `extracted_data/` par défaut (non versionné). Si vous souhaitez conserver d'importantes découvertes dans Git, déplacez manuellement le fichier CSV généré à la racine du projet (voir `undocumented_registers-20260122_020224.csv` comme exemple).

### Inspection ciblée de registres

Pour inspecter une plage spécifique de registres :

```sh
python inspect_register_range.py <adresse_début> <adresse_fin>
```

Exemples :

```sh
# Inspecter les 50 premiers registres (adresses 0-49, registres 1-50)
python inspect_register_range.py 0 49

# Inspecter une zone spécifique suspecte
python inspect_register_range.py 100 150

# Utiliser une adresse IP personnalisée
python inspect_register_range.py 0 49 --ip 192.168.1.100
```

Cet outil affiche :
- Représentations décimale, hexadécimale et binaire
- Interprétation ASCII (si caractères imprimables)
- Valeurs potentielles d'octet IP
- Interprétation en température (valeur signée avec décimale)
- Détection automatique de motifs (adresses IP, chaînes ASCII)

### Cas d'usage

Basé sur les retours de la communauté (voir [discussion #144](https://github.com/alepee/hass-hitachi_yutaki/discussions/144)), ces outils peuvent aider à découvrir :

- **Adresse IP de la passerelle** : Probablement stockée sur 4 registres consécutifs
- **Version du firmware de la passerelle** : Peut compléter les registres 1096-1097 (firmware de l'unité et du contrôleur)
- **Informations système supplémentaires** : Données de configuration et d'état non documentées

## Support

Si vous avez besoin d'aide supplémentaire :

1. Vérifiez que tous les prérequis sont remplis
2. Assurez-vous que la passerelle est accessible sur le réseau
3. Vérifiez les connexions physiques entre la PAC et la passerelle
