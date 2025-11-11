import csv
import datetime
import os
import yaml

VPN_CONFIG_FILE = 'vpn_config.yml'

def generate_ticket():
    now = datetime.datetime.now()
    return f"INC{now.strftime('%Y%m%d')}-{now.strftime('%H%M%S')}"

def sanitize_transform_name(transform_str):
    if transform_str is None:
        return "TRANSFORM_SET_default"
    
    sanitized = transform_str.lower().replace(" ", "_").replace("-", "_")
    return "TRANSFORM_SET_" + sanitized

def process_vpn_csv(file_path):
    vpn_requests = []
    with open(file_path, 'r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            ticket = generate_ticket()
            vpn_requests.append({
                'Ticket': ticket,  # Büyük T
                'WAN_interface': row.get('interface', 'Ethernet4/0'),  # WAN_interface olarak değiştir
                'local_subnet': row.get('local_subnet', '0.0.0.0 0.0.0.0'),
                'partner_name': row.get('partner_name', 'unknown'),
                'peer_ip': row['peer_ip'],
                'phase1_auth': row['phase1_auth'],
                'phase1_encr': row['phase1_encr'],
                'phase1_group': row['phase1_group'],
                'phase1_hash': row['phase1_hash'],
                'phase2_transform': row['phase2_transform'],
                'psk': row.get('psk', 'defaultPSK'),
                'remote_subnet': row.get('remote_subnet', '0.0.0.0 0.0.0.0'),
                # Eski key'leri de uyumluluk için ekle
                'ticket': ticket,
                'interface': row.get('interface', 'Ethernet4/0')
            })
    return vpn_requests

def load_vpn_config():
    if not os.path.exists(VPN_CONFIG_FILE):
        return {'partners': {}}
    
    with open(VPN_CONFIG_FILE, 'r') as f:
        data = yaml.safe_load(f)
        return data if data is not None else {'partners': {}}

def check_existing_partner_tickets(partner_name):
    """Check if partner already has tickets"""
    vpn_data = load_vpn_config()
    
    if 'partners' in vpn_data and partner_name in vpn_data['partners']:
        existing_tickets = list(vpn_data['partners'][partner_name].get('tickets', {}).keys())
        return True, existing_tickets
    
    return False, []

def save_vpn_requests(vpn_requests):
    """Save VPN requests to YAML config file"""
    config_file = 'vpn_config.yml'
    
    # Load existing config or create new
    if os.path.exists(config_file):
        with open(config_file, 'r') as f:
            vpn_data = yaml.safe_load(f) or {}
    else:
        vpn_data = {}
    
    # Ensure partners key exists
    if 'partners' not in vpn_data:
        vpn_data['partners'] = {}
    
    for vpn in vpn_requests:
        partner_name = vpn.get('partner_name', 'Unknown')
        ticket = vpn['ticket']
        
        # Create partner if not exists
        if partner_name not in vpn_data['partners']:
            vpn_data['partners'][partner_name] = {'tickets': {}}
        
        # Add ticket
        vpn_data['partners'][partner_name]['tickets'][ticket] = {
            'WAN_interface': vpn['interface'],
            'peer_ip': vpn['peer_ip'],
            'phase1_auth': vpn['phase1_auth'],
            'phase1_encr': vpn['phase1_encr'],
            'phase1_group': vpn['phase1_group'],
            'phase1_hash': vpn['phase1_hash'],
            'phase2_transform': vpn['phase2_transform'],
            'psk': vpn['psk'],
            'local_subnet': vpn['local_subnet'],
            'remote_subnet': vpn['remote_subnet']
        }
    
    # Save config
    with open(config_file, 'w') as f:
        yaml.dump(vpn_data, f, default_flow_style=False, sort_keys=False)
