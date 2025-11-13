# actions client

import socket
import sys
import pkgutil

import actions

# Collect available actions
available_actions = [name for _, name, _ in pkgutil.iter_modules(actions.__path__)]

# Check args
if len(sys.argv) < 2:
    sys.exit(1)

action2exec: str = sys.argv[1]

# Validate action name
if action2exec not in available_actions:
    sys.exit(1)

args4action: str = " ".join(map(str, sys.argv[2:]))

# Build cmd
send_action_cmd: str = f"{action2exec} {args4action}"

# Send cmd to the daemon.socket
with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as s:
    s.connect("/tmp/sbdots_actions.sock")
    s.sendall(send_action_cmd.encode())

    buffer = ""
    while True:
        try:
            chunk = s.recv(4096).decode("utf-8")  # Receive larger chunks
            if not chunk:  # Connection closed by server
                break
            buffer += chunk

            # Process buffer line by line
            while "\n" in buffer:
                line, buffer = buffer.split("\n", 1)
                if line:  # Only print non-empty lines
                    print(line)
                    sys.stdout.flush()  # Ensure immediate output
        except ConnectionResetError:
            # Server closed connection unexpectedly
            break
        except Exception as e:
            print(f"ERROR: Client socket error: {e}", file=sys.stderr)
            break
