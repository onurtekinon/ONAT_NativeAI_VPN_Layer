import os

def log_action(ticket, partner, interface, status, message=""):
    log_folder = "audit_configs"
    os.makedirs(log_folder, exist_ok=True)
    log_file = os.path.join(log_folder, f"log_{ticket}.txt")
    with open(log_file, 'a') as f:
        f.write(f"Ticket: {ticket}\n")
        f.write(f"Partner: {partner}\n")
        f.write(f"Interface: {interface}\n")
        f.write(f"Status: {status}\n")
        if message:
            f.write(f"Message: {message}\n")
        f.write("\n")
