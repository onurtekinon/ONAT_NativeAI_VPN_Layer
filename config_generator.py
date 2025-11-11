import re
import os
import yaml

R1_CONFIG_PATH = 'devices_configurations/R1.txt'



def find_existing_policy(phase1_encr, phase1_hash, phase1_auth, phase1_group, router_config_path='devices_configurations/R1.txt'):
    """Find existing crypto isakmp policy that matches requirements"""
    if not os.path.exists(router_config_path):
        return None
    
    with open(router_config_path, 'r') as f:
        content = f.read()
    
    # Find all crypto isakmp policies
    policy_pattern = r'crypto isakmp policy (\d+)\s*\n((?:\s+.*\n)*)'
    policies = re.findall(policy_pattern, content)
    
    for policy_num, policy_config in policies:
        # Parse policy configuration
        encr_match = re.search(r'encr (\w+)', policy_config)
        hash_match = re.search(r'hash (\w+)', policy_config)
        auth_match = re.search(r'authentication ([\w-]+)', policy_config)
        group_match = re.search(r'group (\d+)', policy_config)
        
        if (encr_match and encr_match.group(1) == phase1_encr and
            hash_match and hash_match.group(1) == phase1_hash and
            auth_match and auth_match.group(1) == phase1_auth and
            group_match and group_match.group(1) == str(phase1_group)):
            return policy_num
    
    return None

def find_existing_transform_set(phase2_transform, router_config_path='devices_configurations/R1.txt'):
    """Find existing transform set that matches requirements"""
    if not os.path.exists(router_config_path):
        return None
    
    with open(router_config_path, 'r') as f:
        content = f.read()
    
    # Find transform sets that match the phase2_transform
    transform_pattern = rf'crypto ipsec transform-set (\S+) {re.escape(phase2_transform)}'
    match = re.search(transform_pattern, content)
    
    if match:
        return match.group(1)
    
    return None

def get_next_isakmp_policy(encr, auth, group, hash, router_config_path=R1_CONFIG_PATH):
    if not os.path.exists(router_config_path):
        return 10
    
    with open(router_config_path, 'r') as f:
        content = f.read()
    
    existing_policies = re.findall(r'crypto isakmp policy (\d+)', content)
    if existing_policies:
        return max(map(int, existing_policies)) + 1
    return 10

def get_next_crypto_map_seq(router_config_path=R1_CONFIG_PATH):
    if not os.path.exists(router_config_path):
        return 10
    
    with open(router_config_path, 'r') as f:
        content = f.read()
    
    existing_seqs = re.findall(r'crypto map CRYPTO_MAP (\d+)', content)
    if existing_seqs:
        return max(map(int, existing_seqs)) + 10
    return 10

def sanitize_transform_name(transform_str):
    sanitized = transform_str.lower().replace(" ", "_").replace("-", "_")
    return "TRANSFORM_SET_" + sanitized

def generate_cli_config(vpn):
    """Generate CLI configuration for VPN"""
    config = []
    config.append(f"! VPN Configuration for Ticket: {vpn['ticket']}")
    config.append(f"! Partner: {vpn.get('partner_name', 'Unknown')}")
    config.append("")
    
    # Check for existing policy
    existing_policy = find_existing_policy(vpn['phase1_encr'], vpn['phase1_hash'], 
                                         vpn['phase1_auth'], vpn['phase1_group'])
    
    if not existing_policy:
        # Create new policy only if needed
        policy_number = get_next_isakmp_policy(vpn['phase1_encr'], vpn['phase1_auth'], 
                                               vpn['phase1_group'], vpn['phase1_hash'])
        config.append(f"crypto isakmp policy {policy_number}")
        config.append(f" encr {vpn['phase1_encr']}")
        config.append(f" authentication {vpn['phase1_auth']}")
        config.append(f" group {vpn['phase1_group']}")
        config.append(f" hash {vpn['phase1_hash']}")
        config.append("")
    else:
        config.append(f"! Using existing crypto isakmp policy {existing_policy}")
        config.append("")
    
    # PSK
    config.append(f"crypto isakmp key {vpn['psk']} address {vpn['peer_ip']}")
    config.append("")
    
    # Check for existing transform set
    existing_transform = find_existing_transform_set(vpn['phase2_transform'])
    
    if not existing_transform:
        # Create new transform set only if needed
        transform_name = f"TRANSFORM_SET_{vpn['phase2_transform'].replace(' ', '_').replace('-', '_')}"
        config.append(f"crypto ipsec transform-set {transform_name} {vpn['phase2_transform']}")
        config.append("")
    else:
        transform_name = existing_transform
        config.append(f"! Using existing transform set {existing_transform}")
        config.append("")
    
    # Crypto map
    sequence = get_next_crypto_map_seq()
    config.append(f"crypto map CRYPTO_MAP {sequence} ipsec-isakmp")
    config.append(f" description VPN_{vpn['ticket']}_{vpn.get('partner_name', 'Unknown')}")
    config.append(f" set peer {vpn['peer_ip']}")
    config.append(f" set transform-set {transform_name}")
    config.append(f" match address {vpn['ticket']}")
    config.append("")
    
    # Interface
    config.append(f"interface {vpn['interface']}")
    config.append(" crypto map CRYPTO_MAP")
    config.append("")
    
    # ACL
    config.append(f"ip access-list extended {vpn['ticket']}")
    config.append(f" permit ip {vpn['local_subnet']} {vpn['remote_subnet']}")
    
    return "\n".join(config)

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
