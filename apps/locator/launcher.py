import subprocess
import sys
import time

# List your scripts here
scripts = [
    ["python", "server_flask.py"],
    ["python", "server_http.py"],
    ["python", "server_websocket.py"],
    ["python", "overlay.py"]
]

processes = []

try:
    # Start all scripts
    for cmd in scripts:
        print(f"Starting: {' '.join(cmd)}")
        p = subprocess.Popen(cmd)
        processes.append(p)

    print("All services started. Press Ctrl+C to stop everything.")

    # Keep launcher alive
    while True:
        time.sleep(1)

except KeyboardInterrupt:
    print("\nStopping all services...")

    for p in processes:
        p.terminate()

    for p in processes:
        p.wait()

    print("All services stopped.")