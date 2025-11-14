# ONAT Native AI VPN Layer

🔗 Relationship Between VPN Layer and ONAT Core

The ONAT Native AI VPN Layer is a standalone, public-facing module built on top of concepts originating from the ONAT Native AI Core.
However, the Core (Native AI engine, ShinSeal identity layer, deterministic trust pipeline, execution logic) is NOT part of the open-source release and remains fully proprietary.
A lightweight Flask-based orchestration portal for automated Cisco VPN configuration lifecycle management.

## Supported Operations

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
- DMVPN Phase 1 / 2 / 3 ready  

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

Example: `inputs/VPN_Inputs/partners.csv`

```csv
ticket,partner_name,interface,peer_ip,pre_shared_key,transform_set,tunnel_protection
INC20250101,ACME,Gi0/0,203.0.113.10,ACMEKEY,esp-gcm-256,on
```

---

## 💻 Commands (UI “Enter Command” field)

| Command                        | Description                                       |
| ------------------------------ | ------------------------------------------------- |
| `create crypto isakmp sa`      | Creates all configs based on uploaded CSV         |
| `modify crypto isakmp sa ACME` | Updates config for a specific partner             |
| `delete crypto isakmp sa ACME` | Removes all configs for the given partner         |

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

- Never hardcode passwords or keys — use SSH key auth or Ansible Vault.  
- `server.py` supports setting a Flask `SECRET_KEY` via environment variable.

---

## 🧠 Roadmap

- DMVPN Phase 1 / 2 / 3 automatic generator  
- Multi-vendor support (Cisco IOS-XE, ASA, Junos)  
- WebAuth + RBAC integration  
- Optional AI-based config validation  

---

# ⚖️ License Model (Dual Licensing)

## ✔ Public Components — Apache 2.0

The following modules are open-source under **Apache License 2.0**:

- VPN Layer  
- Flask Portal  
- CLI/YAML Generators  
- Demo Tools  

See: **`LICENSE`**

---

## 🔒 Proprietary Components — Closed Source

The following components are **NOT** open source and remain the exclusive IP of **Onur Tekin**:

- ONAT Native AI Core  
- Hardware-Anchored Identity Model (ShinSeal)  
- Deterministic Trust Pipeline  
- Secure Execution Layer  
- Native AI Architecture & Methodology  

These proprietary components require a **separate written commercial license**.

See: **`LICENSE-CORE.md`**

---

# 📄 Apache License 2.0 Notice

```
Copyright © 2025 Onur Tekin — Berlin, Germany

This repository contains two types of components:

1) Public Modules (open source):
   - VPN Layer
   - Flask Portal
   - CLI/YAML Generators
   - Demo Tools
   Licensed under Apache License 2.0.

2) Proprietary Components (closed source):
   - ONAT Native AI Core
   - Hardware-Anchored Identity Model
   - Deterministic Trust Pipeline
   - Secure Execution Layer
   - Native AI Architecture & Methodology
   These components are NOT licensed under Apache 2.0.
   All rights reserved © 2025 Onur Tekin.
   Commercial or derivative use requires a separate license.

Apache License Version 2.0:
http://www.apache.org/licenses/LICENSE-2.0

Distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND.
```

---

# 3️⃣ requirements.txt

```
Flask>=3.0
PyYAML>=6.0
```

---

# 4️⃣ Git Commands

```bash
git add README.md LICENSE LICENSE-CORE.md requirements.txt
git commit -m "docs: update licensing model (Apache + Proprietary Core)"
git push
```
## Licensing Clarification

A previous version of this repository may have incorrectly displayed or inherited
an open-source license template (MIT/Apache) before the ONAT Native AI Core licensing
model was finalized. This was an administrative artifact of early repository
initialization and did not constitute a license grant.

All ONAT Native AI Core components — including the architectural design,
trust pipeline, ShinSeal identity model, execution logic, and derivative technologies —
have always remained proprietary and exclusively owned by Onur Tekin.

Any prior appearance of an open-source license is hereby corrected and superseded
by the ONAT Native AI Core Proprietary License (LICENSE-CORE.md).

> **ONAT™ Native AI Core**  
> Proprietary Technology — Copyright © 2025 Onur Tekin  
> All rights reserved.  
> Unauthorized use, derivative work, or redistribution is prohibited.

