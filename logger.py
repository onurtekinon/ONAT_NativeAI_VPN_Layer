import os
from datetime import datetime

def log_action(ticket, partner_name, interface, status, message="", cli_output="", yaml_output=""):
    """Log VPN actions with CLI and YAML outputs"""
    log_folder = 'audit_configs'
    os.makedirs(log_folder, exist_ok=True)
    
    log_file = os.path.join(log_folder, f'log_{ticket}.txt')
    
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    with open(log_file, 'w') as f:
        f.write(f"Ticket: {ticket}\n")
        f.write(f"Partner: {partner_name}\n")
        f.write(f"Interface: {interface}\n")
        f.write(f"Status: {status}\n")
        f.write(f"Timestamp: {timestamp}\n")
        if message:
            f.write(f"Message: {message}\n")
        f.write("-" * 50 + "\n")
        
        if cli_output:
            f.write("\nCLI OUTPUT:\n")
            f.write("=" * 30 + "\n")
            f.write(cli_output)
            f.write("\n" + "=" * 30 + "\n")
        
        if yaml_output:
            f.write("\nYAML OUTPUT:\n")
            f.write("=" * 30 + "\n")
            f.write(yaml_output)
            f.write("\n" + "=" * 30 + "\n")
