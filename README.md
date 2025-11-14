# ONAT Native AI VPN Layer

A lightweight Flask-based orchestration portal for automated Cisco VPN configuration lifecycle management.

It supports:
- **Create:** `create crypto isakmp sa` (requires CSV)
- **Modify:** `modify crypto isakmp sa <PartnerName>` (requires CSV)
- **Delete:** `delete crypto isakmp sa <PartnerName>`

<p align="center">
  <img src="static/Logo/ONAT_Logo.png" height="64" alt="ONAT Logo"/>
</p>

---

## 🚀 Features
- Generates CLI and YAML configuration outputs  
- Detects interface conflicts automatically  
- Logs each VPN operation with a unique ticket ID  
- Ready for DMVPN Phase 1 / 2 / 3 extensions  

---

## ⚙️ Quickstart
```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python server.py
# open http://127.0.0.1:5001
```

> Note: `inputs/VPN_Inputs/`, `devices_configurations/`, and `audit_configs/` are ignored via `.gitignore`.

---

## 🧩 Example CSV

Example file: `inputs/VPN_Inputs/partners.csv`

```csv
ticket,partner_name,interface,peer_ip,pre_shared_key,transform_set,tunnel_protection
INC20250101,ACME,Gi0/0,203.0.113.10,ACMEKEY,esp-gcm-256,on
```

---

## 💻 Commands (UI “Enter Command” field)

| Command                        | Description                                       |
| ------------------------------ | ------------------------------------------------- |
| `create crypto isakmp sa`      | Creates all configs based on the uploaded CSV     |
| `modify crypto isakmp sa ACME` | Modifies the configuration for a specific partner |
| `delete crypto isakmp sa ACME` | Deletes all configurations for the given partner  |

---

## 📁 Project Structure

```
static/Logo/ONAT_Logo.png     # UI logo
server.py                     # Flask web app
config_generator.py           # CLI config generator
modify_generator.py           # Modify command handler
delete_generator.py           # Delete command handler
conflict_checker.py           # Interface conflict checker
csv_processor.py              # CSV parser
logger.py                     # Log writer
```

---

## 🔐 Security Notes

* Never hardcode passwords or keys — use SSH key auth or Ansible Vault.
* `server.py` supports setting a Flask `SECRET_KEY` via environment variable.

---

## 🧠 Roadmap

* DMVPN Phase 1 / 2 / 3 automatic generator  
* Multi-vendor support (Cisco IOS-XE, ASA, Junos)  
* WebAuth + RBAC integration  
* Optional AI-based config validation  

---

## ⚖️ License Model

### ✔ Public Components — Apache 2.0  
This VPN Layer and all public-facing utilities are licensed under **Apache License 2.0**  
See: `LICENSE`

### 🔒 Proprietary Components (Closed Source)  
The following modules are NOT open-source and are fully owned by Onur Tekin:

- ONAT Native AI Core  
- Hardware-Anchored Identity Model  
- Deterministic Trust Pipeline  
- Secure Execution Layer  
- Native AI Architecture & Methodology  

> These are licensed separately under a proprietary license.  
> See `LICENSE-CORE.md`.

---

## 📄 License
- Public components → Apache 2.0  
- ONAT Native AI Core → Proprietary License (`LICENSE-CORE.md`)
Copyright © 2025 Onur Tekin — Berlin, Germany

This repository contains two types of components:

1) Public Modules (open source):
   - VPN Layer
   - Flask Portal
   - CLI/YAML Generators
   - Demo Tools

   These components are licensed under the Apache License, Version 2.0.

2) Proprietary Components (closed source):
   - ONAT Native AI Core
   - Hardware-Anchored Identity Model
   - Deterministic Trust Pipeline
   - Secure Execution Layer
   - Native AI Architecture & Methodology

   These components are NOT licensed under Apache 2.0.
   All rights reserved © 2025 Onur Tekin.
   Commercial, enterprise, or derivative use requires a separate written license.

-----------------------------------------------------------------------

Apache License
Version 2.0, January 2004
http://www.apache.org/licenses/

Licensed under the Apache License, Version 2.0 (the "License");
you may not use the open-source portion of this repository except in
compliance with the License. You may obtain a copy of the License at:

    http://www.apache.org/licenses/LICENSE-2.0

Distributed under an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND.
See the License for the specific language governing permissions and limitations.

3️⃣ requirements.txt

Flask>=3.0
PyYAML>=6.0

git add README.md LICENSE LICENSE-CORE.md requirements.txt
git commit -m "docs: update licensing model (Apache + Proprietary Core)"
git push
