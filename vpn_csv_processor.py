import csv
import datetime

def generate_ticket():
    now = datetime.datetime.now()
    return f"INC{now.strftime('%Y%m%d')}-{now.strftime('%H%M%S')}"

def process_vpn_csv(file_path):
    vpn_requests = []
    with open(file_path, 'r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            ticket = generate_ticket()
            vpn_requests.append({
                'ticket': ticket,
                'partner_name': row.get('partner_name', 'unknown'),
                'peer_ip': row['peer_ip'],
                'phase1_encr': row['phase1_encr'],
                'phase1_hash': row['phase1_hash'],
                'phase1_auth': row['phase1_auth'],
                'phase1_group': row['phase1_group'],
                'phase2_transform': row['phase2_transform'],
                'psk': row.get('psk', 'defaultPSK'),
                'interface': row.get('interface', 'FastEthernet0/0'),
                'local_subnet': row.get('local_subnet', '0.0.0.0 0.0.0.0'),
                'remote_subnet': row.get('remote_subnet', '0.0.0.0 0.0.0.0')
            })
    return vpn_requests
