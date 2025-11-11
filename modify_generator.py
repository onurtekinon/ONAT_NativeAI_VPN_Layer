import yaml
import csv
import re
import os
from csv_processor import load_vpn_config, generate_ticket
from delete_generator import find_crypto_map_sequence
from logger import log_action

def process_modify_csv(file_path):
    """Process CSV file for modifications"""
    modifications = {}
    
    with open(file_path, 'r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            partner_name = row.get('partner_name', '').strip()
            if not partner_name:
                continue
                
            if partner_name not in modifications:
                modifications[partner_name] = {}
            
            # Sadece boş olmayan değerleri al
            for field, value in row.items():
                if field != 'partner_name' and value and value.strip():
                    modifications[partner_name][field] = value.strip()
    
    return modifications

def modify_partner_config(partner_name, modifications):
    """Modify existing partner configuration"""
    vpn_data = load_vpn_config()
    
    if 'partners' not in vpn_data or partner_name not in vpn_data['partners']:
        return None, f"Partner {partner_name} not found"
    
    partner_tickets = vpn_data['partners'][partner_name]['tickets']
    modify_ticket = generate_ticket()
    
    # Check for actual changes (sadece karşılaştır, değiştirme!)
    actual_changes = {}
    for ticket_id, config in partner_tickets.items():
        for field, new_value in modifications.items():
            if field in config:
                old_value = config.get(field)
                if old_value != new_value:  # Sadece farklı değerler
                    actual_changes[field] = {
                        'old_value': old_value,
                        'added_value': new_value  # new_value yerine added_value
                    }
    
    # Eğer gerçek değişiklik yoksa
    if not actual_changes:
        return "! NO CHANGES DETECTED - All values are same as current configuration", None
    
    # Modify kaydını ekle (ticket'ları değiştirme!)
    if 'modify_history' not in vpn_data['partners'][partner_name]:
        vpn_data['partners'][partner_name]['modify_history'] = {}
    
    # Sadece modify_history'ye ekle
    vpn_data['partners'][partner_name]['modify_history'][modify_ticket] = {
        'changes': actual_changes,
        'affected_tickets': list(partner_tickets.keys()),
        'date': modify_ticket[:8]
    }
    
    # Save updated config (sadece modify_history güncellenecek)
    with open('vpn_config.yml', 'w') as f:
        yaml.dump(vpn_data, f, default_flow_style=False, sort_keys=False)
    
    # CLI komutları için added_value'ları kullan
    new_values = {field: changes['added_value'] for field, changes in actual_changes.items()}
    
    return generate_modify_commands(partner_name, modify_ticket, new_values, partner_tickets), modify_ticket

def get_current_acl_from_router(ticket_id, router_config_path='devices_configurations/R1.txt'):
    """Get current ACL configuration from router"""
    if not os.path.exists(router_config_path):
        return []
    
    with open(router_config_path, 'r') as f:
        content = f.read()
    
    # Find ACL block for this ticket
    acl_pattern = rf'ip access-list extended {ticket_id}\s*\n((?:\s+permit.*\n)*)'
    match = re.search(acl_pattern, content)
    
    if match:
        acl_lines = match.group(1).strip().split('\n')
        return [line.strip() for line in acl_lines if line.strip()]
    
    return []

def generate_modify_commands(partner_name, modify_ticket, new_values, partner_tickets):
    """Generate CLI commands for modifications"""
    if not new_values:
        return f"! NO CHANGES DETECTED FOR PARTNER: {partner_name}"
    
    commands = []
    commands.append(f"! MODIFY CONFIGURATION FOR PARTNER: {partner_name}")
    commands.append(f"! MODIFY TICKET: {modify_ticket}")
    commands.append(f"! MODIFICATIONS: {', '.join(new_values.keys())}")
    commands.append("")
    
    # PSK changes
    if 'psk' in new_values:
        for ticket_id, config in partner_tickets.items():
            peer_ip = config.get('peer_ip')
            if peer_ip:
                commands.append(f"! Update PSK for ticket {ticket_id}")
                commands.append(f"crypto isakmp key {new_values['psk']} address {peer_ip}")
                commands.append("")
    
    # ACL changes - incremental add (no deletion)
    if 'local_subnet' in new_values or 'remote_subnet' in new_values:
        for ticket_id, config in partner_tickets.items():
            # Get current ACL from router
            current_acl = get_current_acl_from_router(ticket_id)
            
            # Use NEW values from modifications, not old config values
            local_subnets = new_values.get('local_subnet', config.get('local_subnet', '')).split('|')
            remote_subnets = new_values.get('remote_subnet', config.get('remote_subnet', '')).split('|')
            
            # Generate new permit statements
            new_permits = []
            for i, local_subnet in enumerate(local_subnets):
                if i < len(remote_subnets):
                    local_subnet = local_subnet.strip()
                    remote_subnet = remote_subnets[i].strip()
                    permit_line = f"permit ip {local_subnet} {remote_subnet}"
                    new_permits.append(permit_line)
            
            # Find only new/different permits
            different_permits = []
            for permit in new_permits:
                if not any(permit.strip() in current_line for current_line in current_acl):
                    different_permits.append(permit)
            
            if different_permits:
                commands.append(f"! Add new ACL entries for ticket {ticket_id}")
                commands.append(f"ip access-list extended {ticket_id}")
                for permit in different_permits:
                    commands.append(f" {permit}")
                commands.append("")
                
                # Add comparison warning
                if current_acl:
                    commands.append(f"! WARNING: Previous ACL entries remain active:")
                    for line in current_acl:
                        commands.append(f"! {line}")
                    commands.append("")
    
    return "\n".join(commands)

def generate_modify_yaml(modify_commands, modify_ticket):
    """Generate Ansible YAML for modify operations"""
    lines = modify_commands.strip().split('\n')
    
    yaml_structure = {
        'gather_facts': 'no',
        'hosts': 'vpn_router',
        'tasks': [
            {
                'name': f'Modify VPN Configuration - Ticket {modify_ticket}',
                'ios_config': {
                    'lines': lines
                }
            }
        ]
    }
    return yaml_structure
