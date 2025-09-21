import os
import re
import pandas as pd
import numpy as np

RESULTS_DIR = "./"
OUTPUT_FILE = os.path.join(RESULTS_DIR, "final_results.csv")


def parse_cpu_mem(stats_file):
    """Parsa CPU% e memoria media da stats.csv, normalizzando la CPU su 800%"""
    cpu_vals, mem_vals = [], []
    with open(stats_file, "r", errors="ignore") as f:
        for line in f:
            line = line.strip()
            if not line or "," not in line:
                continue
            parts = line.split(",")
            if len(parts) < 3:
                continue
            cpu_str = parts[1].strip().replace("%", "")
            mem_str = parts[2].strip().split("/")[0].strip()

            try:
                raw_cpu = float(cpu_str)
                normalized_cpu = raw_cpu / 800 * 100  # normalizza su 0–100%
                cpu_vals.append(normalized_cpu)
            except ValueError:
                continue

            if "MiB" in mem_str:
                mem_vals.append(float(mem_str.replace("MiB", "").strip()))
            elif "GiB" in mem_str:
                mem_vals.append(float(mem_str.replace("GiB", "").strip()) * 1024)

    return (
        np.mean(cpu_vals) if cpu_vals else None,
        np.mean(mem_vals) if mem_vals else None,
    )


def compute_quantile_from_buckets(buckets, total_count, q=0.95):
    """Interpolazione lineare nei bucket Prometheus per stimare il percentile"""
    target = q * total_count
    prev_le, prev_count = 0.0, 0

    for le, count in buckets:
        if count >= target:
            if le == float("inf"):
                return prev_le  # se ultimo bucket è inf, ritorna limite precedente
            bucket_fraction = (
                (target - prev_count) / (count - prev_count)
                if count > prev_count
                else 0
            )
            return prev_le + (le - prev_le) * bucket_fraction
        prev_le, prev_count = le, count

    return float("nan")


def parse_metrics(metrics_file):
    """Parsa avg_latency e p95_latency interpolata da sub_metrics.log"""
    avg_latency = None
    p95_latency = None
    buckets = []
    total_count, total_sum = None, None

    with open(metrics_file, "r") as f:
        for line in f:
            if line.startswith("e2e_latency_bucket"):
                m = re.search(r'le="([^"]+)".*? (\d+)', line)
                if m:
                    le_str, count = m.groups()
                    le = float("inf") if le_str == "+Inf" else float(le_str)
                    buckets.append((le, int(count)))
            elif line.startswith("e2e_latency_count"):
                total_count = int(line.split()[-1])
            elif line.startswith("e2e_latency_sum"):
                total_sum = int(line.split()[-1])

    if total_count and total_count > 0 and total_sum is not None:
        avg_latency = total_sum / total_count
        p95_latency = compute_quantile_from_buckets(buckets, total_count, 0.95)

    return avg_latency, p95_latency


def parse_stdout(stdout_file):
    """Parsa avg throughput dal sub_stdout.log (solo da 10s in poi)"""
    throughputs = []
    with open(stdout_file, "r", errors="ignore") as f:
        for line in f:
            m = re.search(r"(\d+)s .*?recv total=\d+ rate=([\d.]+)/sec", line)
            if m:
                sec, rate = int(m.group(1)), float(m.group(2))
                if sec >= 10:
                    throughputs.append(rate)

    return np.mean(throughputs) if throughputs else None


def main():
    rows = []
    for broker in os.listdir(RESULTS_DIR):
        broker_path = os.path.join(RESULTS_DIR, broker)
        if not os.path.isdir(broker_path):
            continue
        for test in os.listdir(broker_path):
            test_path = os.path.join(broker_path, test)
            if not os.path.isdir(test_path):
                continue

            stats_file = os.path.join(test_path, f"stats_{test}.csv")
            metrics_file = os.path.join(test_path, "sub_metrics.log")
            stdout_file = os.path.join(test_path, "sub_stdout.log")

            avg_cpu, avg_mem = (None, None)
            avg_latency, p95_latency = (None, None)
            avg_throughput = None

            if os.path.exists(stats_file):
                avg_cpu, avg_mem = parse_cpu_mem(stats_file)
            if os.path.exists(metrics_file):
                avg_latency, p95_latency = parse_metrics(metrics_file)
            if os.path.exists(stdout_file):
                avg_throughput = parse_stdout(stdout_file)

            rows.append(
                {
                    "broker": broker,
                    "test": test,
                    "avg_latency_ms": avg_latency,
                    "p95_latency_ms": p95_latency,
                    "avg_throughput_msg_s": avg_throughput,
                    "avg_cpu_percent": avg_cpu,
                    "avg_mem_mb": avg_mem,
                }
            )

    df = pd.DataFrame(rows)
    df.to_csv(OUTPUT_FILE, index=False)
    print(f"✅ Risultati salvati in {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
