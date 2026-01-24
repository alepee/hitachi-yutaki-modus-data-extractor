# Solution: Unique ID pour passerelle Hitachi ATW-MBS-02

## 🎯 Résumé

La passerelle **Hitachi ATW-MBS-02** expose un identifiant unique stable dans les **Input Registers 1-3** (adresses Modbus 0-2).

### Unique ID trouvé
- **Format décimal**: `3846-103-56`
- **Format hexadécimal**: `0F06:0067:0038`
- **Registres Modbus**: Input Registers 1-3 (addresses 0-2)
- **Function Code**: 04 (Read Input Registers)

### Avantages ✅

- ✅ **Compatible Docker** - Pas besoin de la table ARP du système
- ✅ **Stable** - Valeurs identiques sur lectures multiples
- ✅ **Simple** - 3 registres Modbus en lecture seule
- ✅ **Fiable** - Input Registers = informations matériel
- ✅ **Rapide** - Une seule requête Modbus

## 📝 Implémentation pour Home Assistant

### Code Python

```python
from pymodbus.client import ModbusTcpClient

def get_gateway_unique_id(host: str, timeout: int = 3) -> str | None:
    """
    Read unique ID from Hitachi ATW-MBS-02 gateway.
    
    Args:
        host: Gateway IP address or hostname
        timeout: Connection timeout in seconds
    
    Returns:
        Unique ID string (e.g., "3846-103-56") or None if failed
    """
    client = ModbusTcpClient(host, timeout=timeout)
    
    try:
        if not client.connect():
            return None
        
        # Read Input Registers at addresses 0-2
        result = client.read_input_registers(address=0, count=3)
        
        if result.isError() or not hasattr(result, 'registers'):
            return None
        
        # Format as decimal string
        return '-'.join(str(v) for v in result.registers)
        
    except Exception:
        return None
    finally:
        client.close()
```

### Intégration dans config_flow.py

```python
from homeassistant import config_entries
from homeassistant.const import CONF_HOST
import voluptuous as vol

class HitachiYutakiConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Hitachi Yutaki."""
    
    VERSION = 1
    
    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}
        
        if user_input is not None:
            # Test connection and get unique ID
            host = user_input[CONF_HOST]
            
            try:
                # Get unique ID from gateway
                unique_id = await self.hass.async_add_executor_job(
                    get_gateway_unique_id, host
                )
                
                if unique_id:
                    # Set unique ID for this config entry
                    await self.async_set_unique_id(unique_id)
                    self._abort_if_unique_config_entry()
                    
                    # Create config entry
                    return self.async_create_entry(
                        title=f"Hitachi Yutaki ({host})",
                        data=user_input
                    )
                else:
                    errors["base"] = "cannot_connect"
                    
            except Exception:
                errors["base"] = "unknown"
        
        # Show form
        data_schema = vol.Schema({
            vol.Required(CONF_HOST): str,
        })
        
        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            errors=errors
        )
```

## 🧪 Tests de validation

### Test de stabilité

```bash
python test_unique_id_candidates.py
```

**Résultats** (5 lectures consécutives):
- Read 1: `3846-103-56`
- Read 2: `3846-103-56`
- Read 3: `3846-103-56`
- Read 4: `3846-103-56`
- Read 5: `3846-103-56`

✅ **100% stable**

### Tests à effectuer

1. **✅ Stabilité** - Vérifié (5 lectures identiques)
2. **⏳ Persistence** - À tester après redémarrage de la passerelle
3. **⏳ Unicité** - À vérifier avec une 2ème passerelle ATW-MBS-02

## 📊 Données techniques

### Registres Modbus scannés

| Zone | Type | Plage | Résultat |
|------|------|-------|----------|
| 0-999 | Holding (03) | Registres 1-1000 | Config réseau trouvée |
| 0-999 | Input (04) | Registres 1-1000 | **✅ Unique ID trouvé** |
| 1000-1231 | Holding (03) | Registres 1001-1232 | Config pompe à chaleur |

### Input Registers de la passerelle

| Register | Address | Valeur | Hex | Description probable |
|----------|---------|--------|-----|---------------------|
| 1 | 0 | 3846 | 0x0F06 | **ID Part 1** - Version firmware? |
| 2 | 1 | 103 | 0x0067 | **ID Part 2** |
| 3 | 2 | 56 | 0x0038 | **ID Part 3** |
| ... | ... | ... | ... | ... |
| 21 | 20 | 192 | 0x00C0 | IP octet 1 |
| 22 | 21 | 168 | 0x00A8 | IP octet 2 |
| 23 | 22 | 0 | 0x0000 | IP octet 3 |
| 24 | 23 | 4 | 0x0004 | IP octet 4 |

## 🔧 Scripts disponibles

### 1. Scan des Input Registers
```bash
python scan_input_registers.py --start 0 --end 999
```
Résultat: `extracted_data/input_registers-YYYYMMDD_HHMMSS.csv`

### 2. Test de stabilité
```bash
python test_unique_id_candidates.py
```
Teste la stabilité de l'ID sur plusieurs lectures.

### 3. Récupération de l'ID
```bash
python get_gateway_unique_id.py
```
Affiche l'unique ID et le code d'intégration.

## 📚 Contexte de la solution

### Problème initial
Home Assistant nécessite un `unique_id` stable pour chaque config entry. L'IP n'est pas acceptable car elle peut changer.

### Solutions envisagées

1. **❌ Adresse MAC via ARP** 
   - Ne fonctionne pas dans Docker (table ARP isolée)
   - Était la solution initiale proposée

2. **❌ Holding Registers 0-999**
   - Scanné initialement
   - Contient config réseau mais pas d'ID unique stable

3. **✅ Input Registers 0-999** (SOLUTION RETENUE)
   - Scan effectué suite au feedback Docker
   - ID unique trouvé aux registres 1-3
   - Stable et compatible Docker

4. **🔄 Composite ID** (Fallback si besoin)
   - Combinaison de plusieurs registres Holding
   - Moins élégant mais fonctionnel

### Documentation Modbus

Le protocole Modbus TCP supporte théoriquement:
- **65536 registres maximum** par type (0-65535)
- En pratique, la passerelle ATW-MBS-02 utilise:
  - Holding Registers: 0-1231 (config pompe + passerelle)
  - Input Registers: 0-999+ (infos matériel)

## 🎓 Références

- [Home Assistant Config Flow](https://developers.home-assistant.io/docs/config_entries_config_flow_handler)
- [Unique ID Requirements](https://developers.home-assistant.io/docs/config_entries_config_flow_handler#unique-id-requirements)
- [Modbus Protocol](https://www.modbus.org/docs/Modbus_Application_Protocol_V1_1b3.pdf)
- [pymodbus Documentation](https://pymodbus.readthedocs.io/)

## ⚠️ Notes importantes

1. **Validation avec reboot**: Tester la persistence de l'ID après redémarrage de la passerelle
2. **Validation d'unicité**: Si possible, scanner une 2ème passerelle ATW-MBS-02 pour confirmer que l'ID est différent
3. **Gestion d'erreur**: Implémenter un fallback si la lecture échoue (ex: utiliser IP temporairement)
4. **Timeout**: Utiliser un timeout de 3-5 secondes pour la connexion Modbus

## 📞 Support

Pour toute question sur cette implémentation:
1. Consulter les scripts de test dans ce dépôt
2. Vérifier les logs de scan dans `extracted_data/`
3. Référer à `DOCKER_COMPATIBLE_SOLUTION.md` pour le contexte complet
