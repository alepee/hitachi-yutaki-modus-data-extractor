# Solution Unique ID compatible Docker/Container

## ⚠️ Problème avec la solution ARP

**La table ARP ne fonctionne PAS dans un container Docker** car :
- Home Assistant Supervised/Container/OS tourne dans Docker
- La table ARP du container est isolée
- 90%+ des utilisateurs utilisent Docker

❌ **La solution précédente (ARP) n'est pas viable en production**

## 🔍 Investigation : Que contiennent réellement les registres ?

Analysons ce qu'on a trouvé dans le scan des registres 0-999.

### Registres intéressants identifiés

D'après `undocumented_registers-20260122_020224.csv` :

| Registre | Adresse | Valeur | Interprétation possible |
|----------|---------|--------|-------------------------|
| 1 | 0 | 3846 | 0x0F06 - Possible ID modèle/version |
| 2-3 | 1-2 | 103, 56 | ASCII 'g8' - Identifiant ? |
| 7 | 6 | 2 | Configuration |
| 9 | 8 | 13482 | 0x34AA - Valeur stable ? |
| 11 | 10 | 11806 | 0x2E1E |
| 12 | 11 | 12470 | 0x30B6 |
| 21-24 | 20-23 | 192, 168, 0, 4 | **IP actuelle** |
| 41-44 | 40-43 | 13484, 13481, 13485, 13486 | ASCII '4444' - Version ? |

### Registres au-delà de 999

**On n'a pas scanné au-delà !** Peut-être que la MAC ou le S/N sont dans :
- Registres 1000-9999
- Input Registers au lieu de Holding Registers

## 🎯 Solutions viables pour Docker

### Option A : Scanner au-delà de 999 (RECOMMANDÉ)

Il est probable que des infos comme le S/N ou la MAC soient dans des registres > 999.

#### 1. Scanner les Holding Registers 1000-1999

```python
# Extension du scan actuel
python scan_undocumented_registers.py --start 1000 --end 1999
```

#### 2. Scanner les Input Registers

Les Input Registers sont différents des Holding Registers :

```python
from pymodbus.client import ModbusTcpClient

client = ModbusTcpClient(ip)
client.connect()

# Holding Registers (ce qu'on a déjà scanné)
holding = client.read_holding_registers(address=0, count=100)

# Input Registers (PAS ENCORE SCANNÉ !)
input_regs = client.read_input_registers(address=0, count=100)

client.close()
```

### Option B : Créer un identifiant composite stable

Si on ne trouve pas de numéro de série, utiliser une combinaison stable de registres.

#### Critères pour un bon composite

1. **Ne doit PAS inclure l'IP** (change avec DHCP)
2. **Doit être stable** (ne change pas au redémarrage)
3. **Doit être unique** (différent pour chaque passerelle)

#### Candidats possibles

D'après notre scan :

```python
def get_gateway_stable_id(client):
    """
    Create stable unique ID from gateway-specific registers.
    
    Uses multiple registers that are likely factory-programmed
    and unique to each device.
    """
    try:
        # Register 1 (0x0F06) - Possible device ID
        r1 = client.read_holding_registers(0, 1).registers[0]
        
        # Registers 41-44 - ASCII pattern or version
        r41_44 = client.read_holding_registers(40, 4).registers
        
        # Register 9 (0x34AA) - Stable value
        r9 = client.read_holding_registers(8, 1).registers[0]
        
        # Create composite ID
        # Format: MODEL_VERSION_PATTERN
        composite = f"{r1:04x}_{r9:04x}_{''.join(f'{r:04x}' for r in r41_44)}"
        
        return composite
        
    except Exception as e:
        return None

# Example result: "0f06_34aa_34ac34a934ad34ae"
```

**Validation nécessaire :**
- ✅ Tester sur plusieurs passerelles pour vérifier l'unicité
- ✅ Tester après redémarrage pour vérifier la stabilité
- ❌ Problème : On ne sait pas si ces valeurs sont vraiment uniques par appareil

### Option C : IP + Port avec gestion intelligente (FALLBACK)

Selon la [documentation Home Assistant](https://developers.home-assistant.io/docs/config_entries_config_flow_handler#unique-id-requirements), l'IP seule est inacceptable, MAIS on peut l'utiliser avec des limitations connues.

#### Solution avec IP + disclaimer

```python
def get_unique_id_fallback(host, port):
    """
    Fallback unique ID when no stable hardware ID available.
    
    WARNING: This will create duplicate entries if IP changes.
    User will need to remove old entry and add new one.
    """
    # Use IP + Port + model identifier
    return f"hitachi_atwmbs02_{host.replace('.', '_')}_{port}"

# Store in config entry data for future reference
data = {
    CONF_HOST: host,
    CONF_PORT: port,
    "unique_id_method": "ip_based",  # Mark as IP-based
    "warning": "IP-based unique ID - may require reconfiguration if IP changes"
}
```

**Documenter clairement :**
```
⚠️ IMPORTANT: Cette intégration utilise l'adresse IP comme identifiant unique.
Si l'IP de votre passerelle change, vous devrez :
1. Supprimer l'ancienne entrée
2. Reconfigurer avec la nouvelle IP

💡 Recommandation : Configurez une IP statique pour votre passerelle ATW-MBS-02
dans les paramètres DHCP de votre routeur.
```

### Option D : Demander à l'utilisateur

Comme dernier recours, demander à l'utilisateur d'entrer un identifiant :

```python
async def async_step_user(self, user_input=None):
    """Ask user for gateway identification."""
    
    return self.async_show_form(
        step_id="user",
        data_schema=vol.Schema({
            vol.Required(CONF_HOST): str,
            vol.Optional(CONF_PORT, default=502): int,
            vol.Required("gateway_name", default="Gateway 1"): str,
        }),
    )

# Unique ID = hitachi_atwmbs02_gateway_1
# User must use different names for multiple gateways
```

## 🔬 Plan d'action immédiat

### Phase 1 : Investigation (À FAIRE)

1. **Scanner Input Registers 0-999**
   ```bash
   python scan_input_registers.py
   ```

2. **Scanner Holding Registers 1000-2000**
   ```bash
   python scan_undocumented_registers.py --start 1000 --end 2000
   ```

3. **Chercher patterns dans la doc PDF**
   - Relire `doc/Modbus Hitachi registers.pdf`
   - Chercher mentions de "Serial Number", "Device ID", "MAC"

### Phase 2 : Validation

Si on trouve quelque chose :

1. **Tester la stabilité**
   - Redémarrer la passerelle
   - Vérifier que la valeur ne change pas

2. **Tester l'unicité**
   - Idéalement : tester sur 2+ passerelles différentes
   - Vérifier que les valeurs sont différentes

3. **Documenter**
   - Quel registre ?
   - Quelle signification ?
   - Format des données ?

### Phase 3 : Implémentation

Selon ce qu'on trouve :

| Trouvaille | Action |
|------------|--------|
| ✅ Numéro de série trouvé | Utiliser comme unique ID direct |
| ✅ MAC trouvée | Utiliser avec `format_mac()` |
| ✅ ID stable unique trouvé | Utiliser tel quel |
| ❌ Rien trouvé | Option C (IP-based) avec disclaimers |

## 🛠️ Scripts à créer

### 1. Scanner Input Registers

```python
"""scan_input_registers.py"""

from pymodbus.client import ModbusTcpClient
import os
from dotenv import load_dotenv

def scan_input_registers(ip, start=0, end=999):
    """Scan Input Registers (not Holding Registers)."""
    client = ModbusTcpClient(ip, timeout=3)
    
    if not client.connect():
        print(f"Failed to connect to {ip}")
        return []
    
    results = []
    
    for addr in range(start, end + 1):
        try:
            result = client.read_input_registers(address=addr, count=1)
            
            if not result.isError():
                value = result.registers[0]
                results.append((addr + 1, addr, value))
                print(f"Input Register {addr+1} (addr {addr}): {value}")
                
        except Exception as e:
            continue
    
    client.close()
    return results

if __name__ == "__main__":
    load_dotenv()
    ip = os.getenv('MODBUS_IP_ADDRESS')
    
    print(f"Scanning INPUT registers 0-999 on {ip}...")
    results = scan_input_registers(ip, 0, 999)
    
    print(f"\nFound {len(results)} readable input registers")
    
    # Save results
    with open('input_registers.csv', 'w') as f:
        f.write('register,address,value\n')
        for reg, addr, val in results:
            f.write(f'{reg},{addr},{val}\n')
```

### 2. Scanner registres étendus

```python
"""scan_extended_registers.py"""

# Même chose que scan_undocumented_registers.py
# mais pour 1000-2000+
```

### 3. Chercher patterns de serial number

```python
"""find_serial_patterns.py"""

def find_potential_serial_numbers(results):
    """
    Look for patterns that might be serial numbers:
    - 6-12 consecutive registers with non-zero, non-0xFFFF values
    - ASCII strings
    - Unique numeric sequences
    """
    # Implementation...
```

## 📋 Recommandation finale

### Court terme (avant d'avoir plus d'infos)

**Option C avec disclaimers** : Utiliser IP + Port comme unique ID avec :

1. **Documentation claire** du problème
2. **Guide de configuration IP statique** pour l'utilisateur
3. **Avertissement** lors du setup
4. **Code de migration** prêt pour quand on trouvera mieux

```python
# Dans config_flow.py
async def async_step_user(self, user_input=None):
    """Handle user step."""
    if user_input is not None:
        host = user_input[CONF_HOST]
        port = user_input[CONF_PORT]
        
        # Try to find serial number or stable ID
        stable_id = await self._try_get_stable_id(host, port)
        
        if stable_id:
            unique_id = stable_id
        else:
            # Fallback to IP-based
            unique_id = f"atwmbs02_{host.replace('.', '_')}_{port}"
            # Store warning in entry data
            user_input["unique_id_method"] = "ip_based"
        
        await self.async_set_unique_id(unique_id)
        self._abort_if_unique_id_configured()
        
        return self.async_create_entry(...)
```

### Long terme (après investigation)

1. Scanner Input Registers et Holding Registers étendus
2. Demander à la communauté si quelqu'un a plusieurs passerelles
3. Contacter Hitachi support technique
4. Proposer une migration des anciennes entrées vers le nouveau unique ID

## 🎯 Actions immédiates pour vous

1. Je vais créer les scripts de scan Input Registers et Extended Registers
2. On scanne ces nouveaux registres
3. On analyse les résultats pour trouver un ID stable
4. Si rien : on documente la solution IP-based comme temporaire

Voulez-vous que je crée ces scripts de scan maintenant ?
