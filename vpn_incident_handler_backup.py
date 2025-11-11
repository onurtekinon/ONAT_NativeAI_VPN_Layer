import yaml
import os
import re

VPN_CONFIG_FILE = 'vpn_config.yml'
R1_CONFIG_PATH = 'devices_configurations/R1.txt'

def get_existing_isakmp_policies(router_config_path=R1_CONFIG_PATH):
    policies = set()
    if not os.path.exists(router_config_path):
        return policies
    with open(router_config_path, 'r') as f:
        for line in f:
            match = re.match(r'^crypto isakmp policy (\d+)', line.strip())
            if match:
                policies.add(int(match.group(1)))
    return policies

def find_matching_isakmp_policy(encr, auth, group, hash, router_config_path=R1_CONFIG_PATH):
    if not os.path.exists(router_config_path):
        return None
    
    with open(router_config_path, 'r') as f:
        content = f.read()
    
    # ISAKMP policy bloklarını bul
    policy_pattern = r'crypto isakmp policy (\d+)\s*\n((?:\s+.*\n)*)'
    policies = re.findall(policy_pattern, content)
    
    for policy_num, policy_body in policies:
        # Policy içeriğini parse et
        if (f'encr {encr}' in policy_body and
            f'authentication {auth}' in policy_body and
            f'group {group}' in policy_body and
            f'hash {hash}' in policy_body):
            return int(policy_num)
    
    return None

def get_next_isakmp_policy(encr, auth, group, hash, router_config_path=R1_CONFIG_PATH):
    matching_policy = find_matching_isakmp_policy(encr, auth, group, hash, router_config_path)
    if matching_policy:
        return matching_policy

    existing_policies = get_existing_isakmp_policies(router_config_path)
    policy_num = 10
    while policy_num in existing_policies:
        policy_num += 1
    return policy_num

def get_next_acl_number(router_config_path=R1_CONFIG_PATH):
    acl_numbers = []
    if not os.path.exists(router_config_path):
        return 100
    with open(router_config_path, 'r') as f:
        for line in f:
            line = line.strip()
            if line.startswith('access-list'):
                parts = line.split()
                if len(parts) >= 2 and parts[1].isdigit():
                    acl_numbers.append(int(parts[1]))
    if acl_numbers:
        return max(acl_numbers) + 1
    return 100

def get_next_crypto_map_seq(router_config_path=R1_CONFIG_PATH):
    seq_nums = set()
    if not os.path.exists(router_config_path):
        return 10
    with open(router_config_path, 'r') as f:
        for line in f:
            line = line.strip()
            match = re.match(r'^crypto map \S+ (\d+) ipsec-isakmp', line)
            if match:
                seq_nums.add(int(match.group(1)))
    seq = 10
    while seq in seq_nums:
        seq += 10
    return seq

def load_vpn_config():
    if os.path.exists(VPN_CONFIG_FILE):
        with open(VPN_CONFIG_FILE, 'r') as f:
            return yaml.safe_load(f)
    return {'vpns': []}

def check_interface_conflict(interface):
    vpn_data = load_vpn_config()
    for vpn in vpn_data.get('vpns', []):
        if vpn['interface'] == interface:
            return True, vpn['ticket']
    return False, None

def save_vpn_requests(vpn_requests):
    vpn_data = load_vpn_config()
    
    # vpn_data None ise boş dict oluştur
    if vpn_data is None:
        vpn_data = {'vpns': []}
    
    # vpns key'i yoksa veya None ise boş liste oluştur
    if 'vpns' not in vpn_data or vpn_data['vpns'] is None:
        vpn_data['vpns'] = []
    
    # Emin olmak için bir kez daha kontrol
    if vpn_data['vpns'] is None:
        vpn_data['vpns'] = []
    
    vpn_data['vpns'].extend(vpn_requests)
    
    with open(VPN_CONFIG_FILE, 'w') as f:
        yaml.dump(vpn_data, f)

def sanitize_transform_name(transform_str):
    sanitized = transform_str.lower().replace(" ", "_").replace("-", "_")
    return "TRANSFORM_SET_" + sanitized

def transform_set_exists(transform_name, router_config_path=R1_CONFIG_PATH):
    if not os.path.exists(router_config_path):
        return False
    
    with open(router_config_path, 'r') as f:
        content = f.read()
    
    return f"crypto ipsec transform-set {transform_name}" in content

def generate_cli_config(vpn_request):
    ticket = vpn_request['ticket']
    description = f"VPN_{ticket}_{vpn_request.get('partner_name', 'unknown')}"
    warnings = []

    # ISAKMP policy kontrolü
    existing_policy = find_matching_isakmp_policy(
        vpn_request['phase1_encr'],
        vpn_request['phase1_auth'],
        vpn_request['phase1_group'],
        vpn_request['phase1_hash']
    )

    if existing_policy:
        policy_num = existing_policy
        warnings.append(f"Using existing crypto isakmp policy {policy_num}")
        is_new_policy = False
    else:
        policy_num = get_next_isakmp_policy(
            vpn_request['phase1_encr'],
            vpn_request['phase1_auth'],
            vpn_request['phase1_group'],
            vpn_request['phase1_hash']
        )
        is_new_policy = True

    # Transform set kontrolü
    transform_name = sanitize_transform_name(vpn_request['phase2_transform'])
    if transform_set_exists(transform_name):
        warnings.append(f"Using existing crypto ipsec transform-set {transform_name}")
        is_new_transform = False
    else:
        is_new_transform = True

    # CLI config oluştur
    cli_config = ""

    # Uyarıları ekle
    if warnings:
        warning_text = "\n".join([f"! WARNING: {w}" for w in warnings])
        cli_config = warning_text + "\n\n"

    # Sadece yeni policy gerekiyorsa ekle
    if is_new_policy:
        cli_config += f"""crypto isakmp policy {policy_num}
 encr {vpn_request['phase1_encr']}
 authentication {vpn_request['phase1_auth']}
 group {vpn_request['phase1_group']}
 hash {vpn_request['phase1_hash']}

"""

    cli_config += f"""crypto isakmp key {vpn_request['psk']} address {vpn_request['peer_ip']}

"""

    # Sadece yeni transform set gerekiyorsa ekle
    if is_new_transform:
        cli_config += f"""crypto ipsec transform-set {transform_name} {vpn_request['phase2_transform']}

"""

    # Crypto map ve ACL
    seq_num = get_next_crypto_map_seq()
    cli_config += f"""crypto map CRYPTO_MAP {seq_num} ipsec-isakmp
 description {description}
 set peer {vpn_request['peer_ip']}
 set transform-set {transform_name}
 match address {ticket}

interface {vpn_request['interface']}
 crypto map CRYPTO_MAP

ip access-list extended {ticket}
 permit ip {vpn_request['local_subnet']} {vpn_request['remote_subnet']}"""

    return cli_config

def generate_yaml_config(cli_config):
    lines = cli_config.strip().split('\n')
    yaml_structure = {
        'gather_facts': 'no',
        'hosts': 'vpn_router',
        'tasks': [
            {
                'name': 'Apply VPN Configuration',
                'ios_config': {
                    'lines': lines
                }
            }
        ]
    }
    return yaml_structure
