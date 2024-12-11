import paramiko
import os
import re

# Function to parse ~/.ssh/config file
def parse_ssh_config():
    config_file = os.path.expanduser("~/.ssh/config")
    servers = []
    current_server = {}
    with open(config_file, 'r') as f:
        for line in f:
            line = line.strip()
            if line.startswith("Host "):
                if current_server:
                    servers.append(current_server)
                    current_server = {}
                current_server['host'] = re.sub(r'^Host\s+', '', line)
            elif line.startswith("User "):
                current_server['user'] = re.sub(r'^User\s+', '', line)
            elif line.startswith("Hostname ") or line.startswith("HostName "):
                current_server['hostname'] = re.sub(r'^(HostName|Hostname)\s+', '', line)
            elif line.startswith("Port "):
                current_server['port'] = re.sub(r'^Port\s+', '', '', line)
        if current_server:
            servers.append(current_server)
    return servers

# Function to read local ~/.ssh/id_rsa.pub file
def read_local_public_key():
    public_key_file = os.path.expanduser("~/.ssh/id_rsa.pub")
    try:
        with open(public_key_file, 'r') as f:
            public_key = f.read().strip()
            return public_key
    except IOError as e:
        print(f"Error reading local public key file: {e}")
        return None

# Function to SSH to servers and update authorized_keys
def ssh_and_update_authorized_keys(username, password, hostname, public_key):
    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(hostname, username=username, password=password, port=22)
        
        # Append public key to authorized_keys
        stdin, stdout, stderr = client.exec_command(f"echo '{public_key}' > ~/.ssh/authorized_keys")
        error = stderr.read().decode().strip()
        if error:
            print(f"Error updating authorized_keys on {hostname}: {error}")
        else:
            print(f"Public key added to authorized_keys on {hostname}")
        
        client.close()
    except Exception as e:
        print(f"Error connecting to {hostname}: {e}")

# Hardcoded username and password
username = "YOUR_USERNAME_HERE"
password = ""

# Read local public key
public_key = read_local_public_key()
if public_key:
    # Parse SSH config and execute SSH commands
    servers = parse_ssh_config()
    for server in servers:
        if server['host'] != '*':
            hostname = server.get('hostname', server['host'])
            user = server.get('user', username)
            port = int(server.get('port', 22))
            ssh_and_update_authorized_keys(user, password, hostname, public_key)
else:
    print("No valid public key found. Exiting.")
