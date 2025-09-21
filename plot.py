import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# --- Lettura CSV ---
df = pd.read_csv("results/summary.csv")

# Directory per salvare i grafici
os.makedirs("plots", exist_ok=True)

# Lista dei test esclusi p2p
other_tests = [t for t in df['test'].unique() if not t.startswith("p2p")]

# Impostazioni grafiche
sns.set(style="whitegrid")
plt.rcParams.update({'figure.autolayout': True})

# Grafici per test non p2p
for test in other_tests:
    df_test = df[df['test'] == test]
    plt.figure(figsize=(8,5))
    sns.barplot(data=df_test, x="broker", y="latency_avg_ms", ci=None)
    plt.title(f"Test {test} - Latency media per Broker")
    plt.ylabel("Latency media (ms)")
    plt.xlabel("Broker")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(f"plots/{test}_latency.png")
    plt.close()

# Grafico unico per p2p
df_p2p = df[df['test'].str.startswith("p2p")]
plt.figure(figsize=(10,6))
sns.barplot(data=df_p2p, x="qos", y="latency_avg_ms", hue="broker", ci=None)
plt.title("Test p2p - Latency media per QoS e Broker")
plt.ylabel("Latency media (ms)")
plt.xlabel("QoS")
plt.legend(title="Broker", bbox_to_anchor=(1.05, 1), loc='upper left')
plt.tight_layout()
plt.savefig("plots/p2p_latency.png")
plt.close()

print("Grafici generati nella cartella 'plots'")

