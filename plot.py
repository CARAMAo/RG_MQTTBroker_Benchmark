import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os

# ===============================
# Impostazioni globali per grafici IEEE
# ===============================
plt.rcParams.update(
    {
        "font.size": 9,
        "axes.labelsize": 9,
        "axes.titlesize": 9,
        "legend.fontsize": 7,
        "xtick.labelsize": 9,
        "ytick.labelsize": 9,
    }
)

# Carica i dati
df = pd.read_csv("./results/final_results.csv")

if not os.path.isdir("plots"):
    os.mkdir("plots")

# Palette colori
cmap = plt.get_cmap("tab10")


# ===============================
# Funzione grafico separato per singolo test (X = broker)
# ===============================
def plot_single_test(subset, test, metric, ylabel, title, filename):
    brokers = subset["broker"].values
    values = subset[metric].values

    fig, ax = plt.subplots(figsize=(3.5, 2.5))  # singola colonna
    bars = ax.bar(brokers, values)

    # Colori diversi
    for i, bar in enumerate(bars):
        bar.set_color(cmap(i % 10))

    ax.set_ylabel(ylabel)
    ax.set_xticks(np.arange(len(brokers)))
    ax.set_xticklabels(brokers, rotation=45, ha="right")  # Ruota le label
    ax.grid(axis="y", linestyle=":", alpha=0.5)
    plt.tight_layout()
    plt.savefig(f"plots/{filename}.pdf", bbox_inches="tight")
    plt.close()


# ===============================
# Grafici aggregati (multi test)
# ===============================
def plot_barchart(df, tests, labels, metric, ylabel, title, filename):
    brokers = df["broker"].unique()
    x = np.arange(len(labels))
    width = 0.15

    fig, ax = plt.subplots(figsize=(7, 3))  # due colonne
    for i, broker in enumerate(brokers):
        subset = df[df["broker"] == broker].set_index("test")
        values = [
            subset.loc[t, metric] if t in subset.index else float("nan") for t in tests
        ]
        ax.bar(x + i * width, values, width, label=broker, color=cmap(i % 10))

    ax.set_xticks(x + width * (len(brokers) - 1) / 2)
    ax.set_xticklabels(labels)
    ax.set_ylabel(ylabel)
    ax.legend()
    ax.grid(axis="y", linestyle=":", alpha=0.5)
    plt.tight_layout()
    plt.savefig(f"plots/{filename}.pdf", bbox_inches="tight")
    plt.close()


# ===============================
# P2P QoS (aggregati)
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
# P2P QoS (separati per broker)
# ===============================
for test in tests_p2p:
    subset = df[df["test"] == test]
    plot_single_test(
        subset,
        test,
        "avg_latency_ms",
        "Latency (ms)",
        f"{test} Avg Latency",
        f"{test}_latency_avg",
    )
    plot_single_test(
        subset,
        test,
        "p95_latency_ms",
        "Latency (ms)",
        f"{test} 95th Percentile Latency",
        f"{test}_latency_p95",
    )
    plot_single_test(
        subset,
        test,
        "avg_throughput_msg_s",
        "Throughput (msg/s)",
        f"{test} Throughput",
        f"{test}_throughput",
    )

# ===============================
# P2P/Fanin/Fanout (aggregati)
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
# P2P/Fanin/Fanout (separati per broker)
# ===============================
for test in tests_mix:
    subset = df[df["test"] == test]
    plot_single_test(
        subset,
        test,
        "avg_latency_ms",
        "Latency (ms)",
        f"{test} Avg Latency",
        f"{test}_latency_avg",
    )
    plot_single_test(
        subset,
        test,
        "p95_latency_ms",
        "Latency (ms)",
        f"{test} 95th Percentile Latency",
        f"{test}_latency_p95",
    )
    plot_single_test(
        subset,
        test,
        "avg_throughput_msg_s",
        "Throughput (msg/s)",
        f"{test} Throughput",
        f"{test}_throughput",
    )

# ===============================
# Scatterplot CPU vs Memoria
# ===============================
tests = df["test"].unique()
for test in tests:
    subset = df[df["test"] == test]
    fig, ax = plt.subplots(figsize=(3.5, 2.5))
    for idx, row in subset.iterrows():
        ax.scatter(row["avg_cpu_percent"], row["avg_mem_mb"], s=60, label=row["broker"])
        ax.text(
            row["avg_cpu_percent"] * 1.01,
            row["avg_mem_mb"] * 1.01,
            row["broker"],
            fontsize=8,
        )

    ax.set_xlabel("CPU %")
    ax.set_ylabel("Memory (MB)")
    ax.grid(True, linestyle=":", alpha=0.5)
    plt.tight_layout()
    plt.savefig(f"plots/scatter_{test}.pdf", bbox_inches="tight")
    plt.close()

print("✅ Scatterplot per ciascun test salvati in plots/")
print("✅ Tutti i grafici (aggregati e separati) sono stati salvati in plots/")
