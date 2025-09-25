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

# MQTT Broker

- Il **broker** è il cuore del sistema MQTT: gestisce le connessioni, mantiene le subscribe/unsubscribe, riceve messaggi pubblicati e li invia ai destinatari corretti.
- Il broker si occupa anche della persistenza dei messaggi (in accordo con QoS e sessioni), filtra topic e applica politiche di autorizzazione.
