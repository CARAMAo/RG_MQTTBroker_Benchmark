import pandas as pd
import matplotlib.pyplot as plt

# Carica i dati
df = pd.read_csv("./final_results.csv")


# ===============================
# Funzione generica per bar chart
# ===============================
def plot_barchart(df, tests, labels, metric, ylabel, title, filename):
    import numpy as np

    brokers = df["broker"].unique()
    x = np.arange(len(labels))
    width = 0.15

    fig, ax = plt.subplots(figsize=(10, 6))
    for i, broker in enumerate(brokers):
        subset = df[df["broker"] == broker].set_index("test")
        values = [
            subset.loc[t, metric] if t in subset.index else float("nan") for t in tests
        ]
        ax.bar(x + i * width, values, width, label=broker)

    ax.set_xticks(x + width * (len(brokers) - 1) / 2)
    ax.set_xticklabels(labels)
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    ax.legend()
    ax.grid(axis="y", linestyle="--", alpha=0.6)
    plt.tight_layout()
    plt.savefig(f"plots/{filename}.png")
    plt.close()


# ===============================
# Grafici p2p QoS
# ===============================
tests_p2p = ["p2p_qos0", "p2p_qos1", "p2p_qos2"]
labels_p2p = ["QoS 0", "QoS 1", "QoS 2"]

plot_barchart(
    df,
    tests_p2p,
    labels_p2p,
    "avg_latency_ms",
    "Latency (ms)",
    "p2p Avg Latency",
    "p2p_latency_avg",
)
plot_barchart(
    df,
    tests_p2p,
    labels_p2p,
    "p95_latency_ms",
    "Latency (ms)",
    "p2p 95th Percentile Latency",
    "p2p_latency_p95",
)
plot_barchart(
    df,
    tests_p2p,
    labels_p2p,
    "avg_throughput_msg_s",
    "Throughput (msg/s)",
    "p2p Throughput",
    "p2p_throughput",
)

# ===============================
# Grafici p2p, fanin, fanout
# ===============================
tests_mix = ["p2p_qos1", "fanin_qos1", "fanout_qos1"]
labels_mix = ["p2p", "Fan-in", "Fan-out"]

plot_barchart(
    df,
    tests_mix,
    labels_mix,
    "avg_latency_ms",
    "Latency (ms)",
    "Mixed Avg Latency",
    "mixed_latency_avg",
)
plot_barchart(
    df,
    tests_mix,
    labels_mix,
    "p95_latency_ms",
    "Latency (ms)",
    "Mixed 95th Percentile Latency",
    "mixed_latency_p95",
)
plot_barchart(
    df,
    tests_mix,
    labels_mix,
    "avg_throughput_msg_s",
    "Throughput (msg/s)",
    "Mixed Throughput",
    "mixed_throughput",
)

# ===============================
# Scatterplot CPU vs Memoria
# ===============================
tests = df["test"].unique()

for test in tests:
    subset = df[df["test"] == test]

    plt.figure(figsize=(8, 6))

    for idx, row in subset.iterrows():
        plt.scatter(
            row["avg_cpu_percent"], row["avg_mem_mb"], s=100, label=row["broker"]
        )
        plt.text(
            row["avg_cpu_percent"] * 1.01,
            row["avg_mem_mb"] * 1.01,
            row["broker"],
            fontsize=9,
        )

    plt.xlabel("CPU %")
    plt.ylabel("Memory (MB)")
    plt.title(f"CPU vs Memory - {test}")
    plt.grid(True, linestyle="--", alpha=0.5)
    plt.tight_layout()
    plt.savefig(f"plots/scatter_{test}.png")
    plt.close()

print("✅ Scatterplot per ciascun test salvati in results/")

print("✅ Tutti i grafici sono stati salvati in plots/")
