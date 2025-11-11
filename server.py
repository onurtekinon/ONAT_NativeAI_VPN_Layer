from flask import Flask, request, render_template_string
import os
import yaml
from config_generator import generate_cli_config, generate_yaml_config
from conflict_checker import check_interface_conflict
from csv_processor import process_vpn_csv, save_vpn_requests
from logger import log_action
from delete_generator import generate_delete_commands, generate_delete_yaml, remove_partner_from_config
from modify_generator import process_modify_csv, modify_partner_config, generate_modify_yaml

app = Flask(__name__)

# ONAT logo dosya yolu (static altında)
ONAT_LOGO_PATH = "Logo/ONAT_Logo.png"   # static/Logo/ONAT_Logo.png

VPN_INPUTS_FOLDER = os.path.join('inputs', 'VPN_Inputs')
os.makedirs(VPN_INPUTS_FOLDER, exist_ok=True)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Orchestration of Network Automation Portal</title>
    <!-- Favicon olarak ONAT -->
    <link rel="icon" href="{{ url_for('static', filename=logo_path) }}">
    <style>
        body {
            background-color: #f5f5f5;
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 20px;
        }
        .container {
            max-width: 800px;
            margin: 0 auto;
            background-color: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .brand {
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 12px;
            margin-bottom: 16px;
        }
        .brand img {
            height: 40px;
            width: auto;
        }
        h2 {
            color: #333;
            text-align: center;
            margin: 0 0 20px 0;
        }
        .form-group {
            margin-bottom: 20px;
        }
        label {
            display: block;
            margin-bottom: 8px;
            font-weight: bold;
            color: #555;
        }
        input[type="text"], input[type="file"] {
            width: 100%;
            padding: 12px;
            border: 2px solid #ddd;
            border-radius: 5px;
            font-size: 14px;
            box-sizing: border-box;
        }
        input[type="text"]:focus {
            border-color: #ff6600;
            outline: none;
        }
        .submit-btn {
            background-color: #ff6600;
            color: white;
            padding: 15px 30px;
            border: none;
            border-radius: 5px;
            font-size: 16px;
            font-weight: bold;
            cursor: pointer;
            width: 100%;
            margin-top: 10px;
        }
        .submit-btn:hover {
            background-color: #e55a00;
        }
        .output-section {
            margin-top: 40px;
            padding: 20px;
            background-color: #f9f9f9;
            border-radius: 5px;
        }
        .completion-header {
            color: #ff6600;
            font-size: 18px;
            font-weight: bold;
            text-align: center;
            margin-bottom: 20px;
            padding: 10px;
            background-color: #fff3e6;
            border-radius: 5px;
        }
        .output-title {
            font-weight: bold;
            color: #333;
            margin-top: 20px;
            margin-bottom: 10px;
            font-size: 16px;
        }
        pre {
            background-color: #2d2d2d;
            color: #f8f8f8;
            padding: 15px;
            border-radius: 5px;
            overflow-x: auto;
            font-family: 'Courier New', monospace;
            font-size: 13px;
            line-height: 1.4;
        }
        .warning {
            color: #d32f2f;
            font-weight: bold;
            background-color: #ffebee;
            padding: 10px;
            border-radius: 5px;
            margin-top: 15px;
        }
    </style>
</head>
<body>
    <div class="container">
        <!-- ONAT marka alanı -->
        <div class="brand">
            <img src="{{ url_for('static', filename=logo_path) }}" alt="ONAT Logo">
            <h2>🔧 Orchestration of Network Automation Technologies</h2>
        </div>

        <form method="POST" enctype="multipart/form-data">
            <div class="form-group">
                <label>Enter Command:</label>
                <input type="text" name="command" required placeholder="create crypto isakmp sa OR delete crypto isakmp sa PartnerName OR modify crypto isakmp sa PartnerName">
            </div>

            <div class="form-group">
                <label>Upload CSV File:</label>
                <input type="file" name="file">
            </div>

            <input type="submit" value="🔍 Check AI Analyze" class="submit-btn">
        </form>

        {% if output %}
            <div class="output-section">
                <div class="completion-header">
                    ✅ AI Analyze Completed
                </div>

                <div class="output-title">CLI Output</div>
                <pre>{{ output['cli'] }}</pre>

                <div class="output-title">YAML Output</div>
                <pre>{{ output['yaml'] }}</pre>

                {% if output['warning'] %}
                    <div class="warning">
                        <strong>⚠️ WARNING:</strong> {{ output['warning'] }}
                    </div>
                {% endif %}
            </div>
        {% endif %}
    </div>
</body>
</html>
"""

@app.route('/', methods=['GET', 'POST'])
def vpn_portal():
    output = None

    if request.method == 'POST':
        command = request.form['command'].strip()
        file = request.files.get('file')

        # MODIFY
        if command.lower().startswith("modify crypto isakmp sa"):
            parts = command.split()
            if len(parts) >= 5:
                partner_name = parts[4]

                if not file:
                    return "CSV file required for modify command"

                file_path = os.path.join(VPN_INPUTS_FOLDER, file.filename)
                file.save(file_path)

                modifications = process_modify_csv(file_path)

                if partner_name in modifications:
                    modify_commands, modify_ticket = modify_partner_config(
                        partner_name, modifications[partner_name]
                    )

                    if modify_commands:
                        modify_yaml = generate_modify_yaml(modify_commands, modify_ticket)
                        log_action(
                            modify_ticket,
                            partner_name,
                            "ALL",
                            "modified",
                            f"Modified: {', '.join(modifications[partner_name].keys())}",
                            modify_commands,
                            yaml.dump(modify_yaml),
                        )

                        output = {
                            'cli': modify_commands,
                            'yaml': yaml.dump(modify_yaml),
                            'warning': f"Configuration for {partner_name} has been modified",
                        }
                    else:
                        output = {'cli': modify_commands, 'yaml': "", 'warning': f"Partner {partner_name} not found"}
                else:
                    return f"Partner {partner_name} not found in CSV file"
            else:
                return "Invalid Modify Command. Please use: modify crypto isakmp sa PartnerName"

        # DELETE
        elif command.lower().startswith("delete crypto isakmp sa"):
            parts = command.split()
            if len(parts) >= 5:
                partner_name = parts[4]

                delete_commands, delete_ticket = generate_delete_commands(partner_name)

                if delete_ticket:
                    remove_partner_from_config(partner_name)
                    delete_yaml = generate_delete_yaml(delete_commands, delete_ticket)
                    log_action(
                        delete_ticket,
                        partner_name,
                        "ALL",
                        "deleted",
                        "",
                        delete_commands,
                        yaml.dump(delete_yaml),
                    )

                    output = {
                        'cli': delete_commands,
                        'yaml': yaml.dump(delete_yaml),
                        'warning': f"All configurations for {partner_name} have been marked for deletion",
                    }
                else:
                    output = {'cli': delete_commands, 'yaml': "", 'warning': f"Partner {partner_name} not found"}
            else:
                return "Invalid Delete Command. Please use: delete crypto isakmp sa PartnerName"

        # CREATE
        elif command.lower() == "create crypto isakmp sa":
            if not file:
                return "CSV file required for create command"

            file_path = os.path.join(VPN_INPUTS_FOLDER, file.filename)
            file.save(file_path)

            vpn_requests = process_vpn_csv(file_path)
            save_vpn_requests(vpn_requests)

            all_cli, all_yaml, warning_message = "", "", ""

            for vpn in vpn_requests:
                cli_config = generate_cli_config(vpn)
                conflict, existing_ticket = check_interface_conflict(vpn['interface'])
                yaml_config = generate_yaml_config(cli_config)

                all_cli += cli_config + "\\n\\n"
                all_yaml += yaml.dump(yaml_config) + "\\n"

                if conflict:
                    warning_message += f"Interface {vpn['interface']} is already assigned to VPN {existing_ticket}. "

                log_action(
                    vpn['ticket'],
                    vpn.get('partner_name', 'unknown'),
                    vpn['interface'],
                    "processed",
                    warning_message,
                    cli_config,
                    yaml.dump(yaml_config),
                )

            output = {'cli': all_cli, 'yaml': all_yaml, 'warning': warning_message}

        else:
            return "Invalid Command. Please use: 'create crypto isakmp sa', 'delete crypto isakmp sa PartnerName', or 'modify crypto isakmp sa PartnerName'"

    return render_template_string(HTML_TEMPLATE, output=output, logo_path=ONAT_LOGO_PATH)

if __name__ == '__main__':
    app.run(debug=True, port=5001)
