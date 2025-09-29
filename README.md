# Benchmark di broker MQTT

Questo progetto, sviluppato nell'ambito del corso di Reti Geografiche, riguarda il benchmarking di alcune implementazioni di broker MQTT fra le più note utilizzando il tool [_emqtt-bench_](https://github.com/emqx/emqtt-bench) per la raccolta di metriche di **latenza** e **throughput**.
**Docker** è stato utilizzato per l'esecuzione dei broker, permettendo di recuperare informazioni sull'utilizzo di CPU e Memoria tramite il comando <code>docker stats</code>.

In particolare, i broker presi in considerazione sono:

| **Broker**                                                      | **Linguaggio** |
| --------------------------------------------------------------- | -------------- |
| [**Mosquitto**](https://github.com/eclipse-mosquitto/mosquitto) | C              |
| [**EMQX**](https://github.com/emqx/emqx)                        | Erlang/OTP     |
| [**NanoMQ**](https://github.com/nanomq/nanomq)                  | C (NNG)        |
| [**rumqttd**](https://github.com/bytebeamio/rumqtt)             | Rust           |
| [**RMQTT**](https://github.com/rmqtt/rmqtt)                     | Rust           |

## Scenari di Test

Ogni broker viene testato in due scenari principali, eseguendo ciascuna configurazione possibile per 5 minuti:

### Architettura Pub/Sub

In questo scenario, andiamo a misurare le performance del broker in termini di **latenza**(ms), **throughput** (msg/sec) e utilizzo di CPU e Memoria utilizzando diverse architetture fondamentali Pub/Sub. Il workload prevede un payload fisso di 64 byte e un publishing rate di 20 msg/sec per ciascun publisher:

#### Point-to-Point (P2P)

Ogni publisher comunica con un solo subscriber, attraverso un topic dedicato:

- 100 publishers
- 100 topic
- 100 subscribers

#### Fan-In

Architettura di aggregazione, in cui un solo subscriber si iscrive a tutti i topic disponibili:

- 100 publishers
- 100 topic
- 1 subscriber

#### Fan-Out

Quest'architettura riguarda l'invio di traffico broadcast da parte di un publisher a più subscriber iscritti allo stesso topic:

- 1 publisher
- 1 topic
- 100 subscribers

### QoS

In questo scenario, andiamo a misurare le performance del broker in termini di **latenza**(ms), **throughput** (msg/sec) e utilizzo di CPU e Memoria sulle varie impostazioni di QoS MQTT (0, 1, 2) utilizzando un'architettura base Point-to-Point con 100 publisher, 100 topic e 100 subscriber. Il workload prevede un payload fisso di 64 byte e un publishing rate di 20 msg/sec per ciascun publisher.

---

### Prerequisiti

Per eseguire i benchmark è necessario disporre di un ambiente con i seguenti requisiti:

- **Sistema operativo**: Linux o macOS (consigliato per la compatibilità con gli script shell e Docker).

- **Docker**: installato e funzionante, per l’esecuzione dei broker MQTT in container

- **Python 3.8+**: utilizzato per l’analisi e l’aggregazione dei log dei benchmark tramite lo script `parse_results.py`

  - (OPZIONALE) per la generazione dei grafici tramite lo script `plot.py` sono richieste anche alcune librerie Python (es. `pandas`, `matplotlib`) che possono essere installate con:
    ```bash
    pip install pandas matplotlib
    ```

La repository contiene i seguenti file:

- <code>MQTT_Broker_report.pdf</code>: paper del progetto;
- <code>run_benchmarks.sh</code>: script di orchestrazione dei container, automatizza la procedura di benchmark in locale, ripetendo i vari test e salvando i log nella cartella <code>results/</code>
- <code>parse_results.py</code>: script di aggregazione dei risultati, fornisce in output un unico file `final_results.csv` che contiene i risultati di tutti i test
- `plot.py`: script di generazione dei grafici, a partire dal file `final_results.csv`;

#### Esempio

    ```bash
    git clone https://github.com/CARAMAo/RG_MQTTBroker_Benchmark

    cd RG_MQTTBroker_Benchmark

    ./run_benchmarks.sh #esecuzione dei test

    python parse_results.py #analisi dei log

    python plot.py #OPZIONALE generazione dei grafici

    ```
