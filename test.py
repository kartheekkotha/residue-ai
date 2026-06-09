import subprocess
import time
import datetime
import os

def get_network_bytes():
    """Returns (ibytes, obytes) for en0 on macOS."""
    try:
        # -I en0: filter for en0, -b: show bytes
        output = subprocess.check_output(["netstat", "-I", "en0", "-b", "-n"], text=True)
        lines = output.strip().split('\n')
        if len(lines) > 1:
            # The second line contains the data for en0
            # Name  Mtu   Network       Address            Ipkts Ierrs     Ibytes    Opkts Oerrs     Obytes  Coll
            parts = lines[1].split()
            # Parts mapping:
            # 0: en0, 1: mtu, 2: network, 3: address, 4: ipkts, 5: ierrs, 6: ibytes, 7: opkts, 8: oerrs, 9: obytes
            return int(parts[6]), int(parts[9])
    except Exception as e:
        return 0, 0

def ping_google():
    """Pings google.com and returns the latency."""
    try:
        output = subprocess.check_output(["ping", "-c", "1", "-W", "2000", "google.com"], text=True)
        for line in output.splitlines():
            if "time=" in line:
                return line.split("time=")[1].split(" ms")[0].strip() + "ms"
    except Exception:
        return "Timeout"
    return "Error"

log_file = "network_log.txt"

if not os.path.exists(log_file):
    with open(log_file, "w") as f:
        f.write("Timestamp | Ping Latency | Inbound Δ | Outbound Δ\n")
        f.write("-" * 60 + "\n")

last_in, last_out = get_network_bytes()

while True:
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ping_val = ping_google()
    curr_in, curr_out = get_network_bytes()
    
    # Calculate bytes transferred in the last interval
    # Note: Handles counters resetting if necessary (simplistic)
    in_diff = curr_in - last_in if curr_in >= last_in else curr_in
    out_diff = curr_out - last_out if curr_out >= last_out else curr_out
    
    log_entry = f"{now} | {ping_val:>12} | {in_diff:>10} B | {out_diff:>10} B\n"
    
    with open(log_file, "a") as f:
        f.write(log_entry)
        f.flush()
    
    last_in, last_out = curr_in, curr_out
    time.sleep(60)
