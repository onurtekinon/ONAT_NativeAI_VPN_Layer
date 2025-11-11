# utils.py
import os
import re
import json
import yaml
import subprocess

def parse_incident(file_path):
    incident_number = "unknown"
    file_type = "unknown"
    if not os.path.exists(file_path):
        print(f"[ERROR] {file_path} not found!")
        return incident_number, file_type
    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            if "incident_number:" in line.lower():
                incident_number = line.split(":", 1)[1].strip()
            elif "file_type:" in line.lower():
                file_type = line.split(":", 1)[1].strip().lower()
    return incident_number, file_type

def log_actions(incident_number, file_type, status="success", message=""):
    action_log_path = f"inputs/VLAN_Inputs/action_list_of({incident_number}).txt"
    with open(action_log_path, 'a', encoding="utf-8") as f:
        f.write(f"Incident: {incident_number}\n")
        f.write(f"File Type: {file_type}\n")
        f.write(f"Status: {status}\n")
        if message:
            f.write(f"Message: {message}\n")
        f.write("\n")
    print(f"[LOG] Log written to {action_log_path}")

# Diğer ortak fonksiyonlar da buraya eklenebilir...
