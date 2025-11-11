import os
import re
import yaml
from datetime import datetime
from csv_processor import load_vpn_config, generate_ticket
from logger import log_action

def generate_ticket():
    """Generate ticket number based on current timestamp"""
    now = datetime.now()
    return f"INC{now.strftime('%Y%m%d-%H%M%S')}"

def load_vpn_config():
    """Load VPN configuration from YAML file"""
    config_file = 'vpn_config.yml'
    if os.path.exists(config_file):
        with open(config_file, 'r') as f:
            return yaml.safe_load(f) or {}
    return {}

def find_partner_configs(partner_name, vpn_config_file='vpn_config.yml'):
    """Find all configurations for a specific partner"""
    vpn_data = load_vpn_config()
    
    if 'partners' not in vpn_data or partner_name not in vpn_data['partners']:
        return None, f"Partner {partner_name} not found in configuration"
    
    partner_tickets = vpn_data['partners'][partner_name]['tickets']
    return partner_tickets, None

def generate_delete_commands(partner_name):
    """Generate delete commands for a partner"""
    vpn_data = load_vpn_config()
    
    if 'partners' not in vpn_data or partner_name not in vpn_data['partners']:
        return f"Partner {partner_name} not found", None
    
    partner_tickets = vpn_data['partners'][partner_name]['tickets']
    delete_ticket = generate_ticket()
    
    commands = []
    commands.append(f"! DELETE CONFIGURATION FOR PARTNER: {partner_name}")
    commands.append(f"! DELETE TICKET: {delete_ticket}")
    commands.append(f"! DATE: {delete_ticket[:8]}")
    commands.append("")
    
    for ticket_id, config in partner_tickets.items():
        commands.append(f"! Deleting configuration for ticket: {ticket_id}")
        
        # Find and delete crypto map sequence
        sequence = find_crypto_map_sequence(ticket_id)
        if sequence:
            commands.append(f"no crypto map CRYPTO_MAP {sequence} ipsec-isakmp")
        
        # Delete PSK with actual key value
        peer_ip = config.get('peer_ip')
        psk = config.get('psk')
        if peer_ip and psk:
            commands.append(f"no crypto isakmp key {psk} address {peer_ip}")
        
        # Delete ACL
        commands.append(f"no ip access-list extended {ticket_id}")
        commands.append("")
    
    commands.append("! NOTE: Remove 'crypto map CRYPTO_MAP' from interface if no other VPNs exist")
    commands.append("! interface <interface_name>")
    commands.append("! no crypto map CRYPTO_MAP")
    
    return "\n".join(commands), delete_ticket

def find_crypto_map_sequence(ticket_id, router_config_path='devices_configurations/R1.txt'):
    """Find crypto map sequence number for a given ticket"""
    if not os.path.exists(router_config_path):
        return None
    
    with open(router_config_path, 'r') as f:
        content = f.read()
    
    # Find crypto map with description containing ticket_id
    pattern = rf'crypto map CRYPTO_MAP (\d+) ipsec-isakmp\s*\n\s*description VPN_{ticket_id}'
    match = re.search(pattern, content)
    
    if match:
        return match.group(1)
    
    return None

def remove_partner_from_config(partner_name):
    """Remove partner from vpn_config.yml"""
    vpn_data = load_vpn_config()
    
    if 'partners' in vpn_data and partner_name in vpn_data['partners']:
        del vpn_data['partners'][partner_name]
        
        with open('vpn_config.yml', 'w') as f:
            yaml.dump(vpn_data, f, default_flow_style=False, sort_keys=False)
        
        return True
    
    return False

def generate_delete_yaml(commands, ticket):
    """Generate YAML structure for delete commands"""
    return {
        'delete_action': {
            'ticket': ticket,
            'commands': commands.split('\n'),
            'timestamp': datetime.now().isoformat()
        }
    }
