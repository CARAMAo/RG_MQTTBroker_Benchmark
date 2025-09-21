import os
import re
import pandas as pd

BASE_DIR = "results"

RECV_RE = re.compile(r"^recv (\d+)")
COUNT_RE = re.compile(r"^e2e_latency_count (\d+)")
SUM_RE = re.compile(r"^e2e_latency_sum (\d+)")
TEST_DURATION = 50
def parse_sub_log(path):
    """Parsa recv, count e sum e calcola lat_avg e throughput medio"""
    recv_val, count_val, sum_val = None, None, None

    with open(path) as f:
        for line in f:
            if m := RECV_RE.match(line):
                recv_val = int(m.group(1))
            elif m := COUNT_RE.match(line):
                count_val = int(m.group(1))
            elif m := SUM_RE.match(line):
                sum_val = int(m.group(1))

    if count_val is None or sum_val is None or recv_val is None:
        raise ValueError(f"File {path} incompleto o malformattato")

    lat_avg = sum_val / count_val if count_val > 0 else None
    throughput = recv_val / TEST_DURATION  # media messaggi/s
    return recv_val, lat_avg, throughput

def parse_stats_csv(path):
    """Media CPU e Memoria da docker stats"""
    cpu_vals, mem_vals = [], []
    with open(path) as f:
        for line in f:
            parts = line.strip().split(",")
            if len(parts) < 3:
                continue
            cpu_str, mem_str = parts[1], parts[2]
            try:
                cpu_vals.append(float(cpu_str.strip("%")))
                mem_vals.append(float(mem_str.split()[0].replace("MiB","")))
            except:
                continue
    return (
        sum(cpu_vals) / len(cpu_vals) if cpu_vals else None,
        sum(mem_vals) / len(mem_vals) if mem_vals else None,
    )

rows = []
for root, dirs, files in os.walk(BASE_DIR):
    if "sub_metrics.log" in files and any(f.startswith("stats_") for f in files):
        parts = root.split(os.sep)
        if len(parts) < 4:
            continue
        _, ts, broker, test = parts
        qos = None
        if "qos" in test:
            qos = test.split("qos")[-1]

        sub_log = os.path.join(root, "sub_metrics.log")
        stats_file = [f for f in files if f.startswith("stats_")][0]
        stats_path = os.path.join(root, stats_file)

        recv_val, lat_avg, throughput_avg = parse_sub_log(sub_log)
        cpu_avg, mem_avg = parse_stats_csv(stats_path)

        rows.append({
            "broker": broker,
            "test": test,
            "qos": qos,
            "recv": recv_val,
            "latency_avg_ms": lat_avg,
            "throughput_avg_msg_s": throughput_avg,
            "cpu_avg_percent": cpu_avg,
            "mem_avg_MB": mem_avg,
        })

df = pd.DataFrame(rows)

ts_file = os.path.join(BASE_DIR, "summary.csv")
df.to_csv(ts_file, index=False)
print(f">>> Dati scritti in {ts_file}")
print(df)

