import os
import yaml
import re

VPN_CONFIG_FILE = 'vpn_config.yml'
R1_CONFIG_PATH = 'devices_configurations/R1.txt'

def check_interface_conflict(interface):
    if not os.path.exists(VPN_CONFIG_FILE):
        return False, None
    
    try:
        with open(VPN_CONFIG_FILE, 'r') as f:
            vpn_data = yaml.safe_load(f)
        
        if vpn_data and 'vpns' in vpn_data:
            for vpn in vpn_data['vpns']:
                if vpn.get('interface') == interface:
                    return True, vpn.get('ticket', 'unknown')
        
        return False, None
    except:
        return False, None

def check_duplicate_vpn(peer_ip, remote_subnet):
    """Check if VPN with same peer_ip and remote_subnet already exists in R1 router config"""
    if not os.path.exists(R1_CONFIG_PATH):
        return False, None
    
    try:
        with open(R1_CONFIG_PATH, 'r') as f:
            content = f.read()
        
        # R1'de bu peer_ip için crypto isakmp key var mı?
        if f"crypto isakmp key" in content and peer_ip in content:
            # Bu peer_ip için mevcut ticket'ı bul
            isakmp_pattern = f"crypto isakmp key .* address {re.escape(peer_ip)}"
            if re.search(isakmp_pattern, content):
                return True, "R1_EXISTING"
        
        return False, None
    except:
        return False, None

def check_r1_peer_exists(peer_ip):
    """Check if peer IP already exists in R1 config"""
    if not os.path.exists(R1_CONFIG_PATH):
        return False
    
    try:
        with open(R1_CONFIG_PATH, 'r') as f:
            content = f.read()
        
        return f"address {peer_ip}" in content
    except:
        return False

def check_r1_acl_subnet_exists(remote_subnet):
    """Check if remote subnet already exists in R1 ACLs"""
    if not os.path.exists(R1_CONFIG_PATH):
        return False
    
    try:
        with open(R1_CONFIG_PATH, 'r') as f:
            content = f.read()
        
        return remote_subnet in content
    except:
        return False

def check_partner_conflict(partner_name):
    """Check if partner already has existing tickets"""
    from csv_processor import check_existing_partner_tickets
    
    has_tickets, existing_tickets = check_existing_partner_tickets(partner_name)
    
    if has_tickets:
        return True, existing_tickets
    
    return False, []
