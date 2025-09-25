---
marp: true
theme: beam
paginate: true
_class: lead
---

<!-- _class: title -->

# Benchmarking di broker MQTT open-source

Pasquale Caramante  
Università degli Studi di Salerno  
Corso di Reti Geografiche: Struttura,Analisi e Prestazioni  
Laurea Magistrale in Informatica - LM 18

---

# MQTT

- MQTT è un protocollo di messaggistica _lightweight_ basato su publish/subscribe, pensato per dispositivi con risorse limitate e reti con larghezza di banda ridotta.
- Standardizzato da OASIS / ISO.
- Consente la comunicazione bi-direzionale fra device e cloud/applicazioni, disaccoppiando mittenti e destinatari attraverso l’uso di topic.
- Caratteristiche chiave:
  - Minimale overhead, adatto a dispositivi embedded;
  - Tre livelli di QoS per garantire affidabilità in reti instabili;
  - Supporto per sessioni persistenti, messaggi “retained”, _Last Will_);
  - Sicurezza via TLS/SSL, autenticazione e autorizzazione;

---

<style scoped>section{font-size:25px;}
    .header{font-size:30px;}
</style>

# MQTT Workflow

1. Connessione
   - Il client apre una **connessione TCP** (opzionalmente con TLS) verso il broker;
   - Il client stabilisce una **sessione MQTT**, inviando un pacchetto <code>CONNECT</code> al broker;
1. Publish/Subscribe
   - Il client può iscriversi (<code>SUBSCRIBE</code>) e/o pubblicare (<code>PUBLISH</code>) messaggi su un topic specifico;
1. Routing
   - Il broker distribuisce i messaggi ai client che si sono iscritti a quel topic, rispettando le regole di QoS.
1. Disconnessione
   - Quando un client si disconnette “normalmente” invia un messaggio <code>DISCONNECT</code> al broker;
   - Se la disconnessione è anomala il broker può pubblicare un **Last Will** predefinito;

---

# QoS 0 — At most once

- Messaggio consegnato **al massimo una volta**;  
- Nessuna conferma di ricezione;  
- È la modalità più veloce ma non garantisce affidabilità.  

![QoS0](URL_DELL_IMMAGINE)

---

# QoS 1 — At least once

- Messaggio consegnato **almeno una volta**;  
- Richiede conferma di ricezione con pacchetto **PUBACK**;  
- Possibile duplicazione dei messaggi.  

![QoS1](URL_DELL_IMMAGINE)

---

# QoS 2 — Exactly once

- Messaggio consegnato **esattamente una volta**;  
- Richiede un handshake a quattro fasi (PUBREC, PUBREL, PUBCOMP);  
- Massima affidabilità ma con overhead maggiore.  

![QoS2](URL_DELL_IMMAGINE)

---

# MQTT Broker

- Il **broker** è il cuore del sistema MQTT: gestisce le connessioni, le sessioni e i topic, instradando i messaggi ricevuti ai destinatari corretti;
- Le prestazioni di un broker possono essere influenzate da diversi fattori:
  - Configurazione HW/SW;
  - Implementazione del broker;
  - Configurazione MQTT;
  - Architettura Pub/Sub;

---

# Obiettivi

- Testare diverse implementazioni di broker MQTT;  
- Confrontare le prestazioni in termini di:  
  - **Latenza end-to-end**;  
  - **Throughput dei messaggi**;  
  - **Consumo di CPU**;  
  - **Consumo di memoria**.  

---

# Metodologia — emqtt-bench

- **emqtt-bench** è un tool di benchmarking MQTT che permette di simulare publisher e subscriber, raccogliendo metriche di latenza e throughput.  
- Permette di configurare:
  - Numero di client;
  - Frequenza di pubblicazione;
  - Dimensione del payload;
  - Parametri di QoS.

---

# Esempio

```bash
emqtt_bench pub -h localhost -p 1883 -t test/topic -c 100 -q 1 -I 100
```
```bash
emqtt_bench sub -h localhost -p 1883 -t test/topic -c 100 -q 1
```
