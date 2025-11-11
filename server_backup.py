from flask import Flask, request, render_template_string
import os
import yaml
import csv
from vpn_incident_handler import check_interface_conflict, save_vpn_requests, generate_cli_config, generate_yaml_config
from action_logger import log_action

app = Flask(__name__)

VPN_INPUTS_FOLDER = os.path.join('inputs', 'VPN_Inputs')
os.makedirs(VPN_INPUTS_FOLDER, exist_ok=True)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>VPN Automation Portal</title>
</head>
<body>
    <h2>VPN Automation Portal</h2>
    <form method="POST" enctype="multipart/form-data">
        <label>Enter Command:</label><br>
        <input type="text" name="command" size="50" required><br><br>

        <label>Upload VPN CSV:</label><br>
        <input type="file" name="file" required><br><br>

        <input type="submit" value="Submit">
    </form>

    {% if output %}
        <h3>CLI Output</h3>
        <pre>{{ output['cli'] }}</pre>

        <h3>YAML Output</h3>
        <pre>{{ output['yaml'] }}</pre>

        {% if output['warning'] %}
            <p style="color:red;"><strong>WARNING:</strong> {{ output['warning'] }}</p>
        {% endif %}
    {% endif %}
</body>
</html>
"""

def process_vpn_csv(file_path):
    vpn_requests = []
    with open(file_path, 'r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        from datetime import datetime
        for row in reader:
            ticket = f"INC{datetime.now().strftime('%Y%m%d')}-{datetime.now().strftime('%H%M%S')}"
            vpn_requests.append({
                'ticket': ticket,
                'peer_ip': row['peer_ip'],
                'phase1_encr': row['phase1_encr'],
                'phase1_hash': row['phase1_hash'],
                'phase1_auth': row['phase1_auth'],
                'phase1_group': row['phase1_group'],
                'phase2_transform': row['phase2_transform'],
                'psk': row.get('psk', 'defaultPSK'),
                'interface': row.get('interface', 'FastEthernet0/0'),
                'local_subnet': row.get('local_subnet', '0.0.0.0 0.0.0.0'),
                'remote_subnet': row.get('remote_subnet', '0.0.0.0 0.0.0.0'),
                'partner_name': row.get('partner_name', 'unknown')
            })
    return vpn_requests

@app.route('/', methods=['GET', 'POST'])
def vpn_portal():
    output = None

    if request.method == 'POST':
        command = request.form['command'].strip()
        file = request.files['file']

        if command.lower() != "create crypto isakmp sa":
            return "Invalid Command. Please type: create crypto isakmp sa"

        file_path = os.path.join(VPN_INPUTS_FOLDER, file.filename)
        file.save(file_path)

        vpn_requests = process_vpn_csv(file_path)
        save_vpn_requests(vpn_requests)

        all_cli = ""
        all_yaml = ""
        warning_message = ""

        for vpn in vpn_requests:
            cli_config = generate_cli_config(vpn)
            conflict, existing_ticket = check_interface_conflict(vpn['interface'])

            yaml_config = generate_yaml_config(cli_config)

            all_cli += cli_config + "\n\n"
            all_yaml += yaml.dump(yaml_config) + "\n"

            if conflict:
                warning_message += f"Interface {vpn['interface']} is already assigned to VPN {existing_ticket}. "

            log_action(vpn['ticket'], vpn.get('partner_name', 'unknown'), vpn['interface'], "processed", warning_message)

        output = {'cli': all_cli, 'yaml': all_yaml, 'warning': warning_message}

    return render_template_string(HTML_TEMPLATE, output=output)

if __name__ == '__main__':
    app.run(debug=True)
