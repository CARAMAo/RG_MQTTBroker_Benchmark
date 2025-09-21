#!/usr/bin/env bash
set -euo pipefail

BROKERS=("mosquitto" "emqx" "nanomq" "rumqttd" "rmqtt")
#BROKERS=("rumqttd" "rmqtt")
DURATION=${DURATION:-60}         # durata test in secondi
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BASE_OUTDIR=results/$TIMESTAMP



function start_broker() {
  local broker=$1
  echo ">>> Avvio broker $broker ..."
  docker compose up -d $broker
  sleep 10
}

function stop_all() {
  echo ">>> Stop di tutti i servizi..."
  docker compose down
}

function collect_stats() {
  local broker=$1
  local tag=$2
  docker stats $broker \
    --no-stream=false \
    --format "{{.Container}},{{.CPUPerc}},{{.MemUsage}},{{.NetIO}},{{.BlockIO}},{{.PIDs}}" \
    > "$BASE_OUTDIR/$broker/$tag/stats_${tag}.csv" &
  echo $!
}

function wait_and_stop() {
  local tag=$1
  local services="$2"
  local stats_pid=$3

  sleep $DURATION
  docker compose stop $services
  kill $stats_pid || true
  wait $stats_pid 2>/dev/null || true
}


function run_p2p() {
  local broker=$1
  local qos=$2
  local tag="p2p_qos${qos}"
  mkdir -p "$BASE_OUTDIR/$broker/$tag"

  echo "### [$broker] Point-to-point (100 pub, 100 topic, 100 sub) QoS=$qos"
  local stats_pid=$(collect_stats $broker $tag)

  BROKER_HOST=$broker NUM_SUB=100 QOS=$qos TOPIC_PATTERN_SUB="test/p2p/%i" RESTAPI=1 docker compose up -d sub
  sleep 5

  BROKER_HOST=$broker NUM_PUB=100 QOS=$qos PUB_INTERVAL=5 TOPIC_PATTERN_PUB="test/p2p/%i" docker compose up -d pub

  sleep $DURATION
  curl -s http://localhost:8080/metrics > "$BASE_OUTDIR/$broker/$tag/sub_metrics.log"
  docker logs sub > "$BASE_OUTDIR/$broker/$tag/sub_stdout.log" 2>&1

  docker compose down pub sub
  kill $stats_pid || true
}

function run_fanin() {
  local broker=$1
  local qos=$2
  local tag="fanin_qos${qos}"
  mkdir -p "$BASE_OUTDIR/$broker/$tag"

  echo "### [$broker] Fan-in (100 pub, 100 topic, 1 sub) QoS=$qos"
  local stats_pid=$(collect_stats $broker $tag)

  BROKER_HOST=$broker NUM_SUB=1 QOS=$qos TOPIC_PATTERN_SUB="test/fanin/#" RESTAPI=1 docker compose up -d sub
  sleep 5

  BROKER_HOST=$broker NUM_PUB=100 QOS=$qos PUB_INTERVAL=5 TOPIC_PATTERN_PUB="test/fanin/%i" docker compose up -d pub

  sleep $DURATION
  curl -s http://localhost:8080/metrics > "$BASE_OUTDIR/$broker/$tag/sub_metrics.log"
  docker logs sub > "$BASE_OUTDIR/$broker/$tag/sub_stdout.log" 2>&1

  docker compose down pub sub
  kill $stats_pid || true
}

function run_fanout() {
  local broker=$1
  local qos=$2
  local tag="fanout_qos${qos}"
  mkdir -p "$BASE_OUTDIR/$broker/$tag"

  echo "### [$broker] Fan-out (1 pub, 1 topic, 100 sub) QoS=$qos"
  local stats_pid=$(collect_stats $broker $tag)

  BROKER_HOST=$broker NUM_SUB=100 QOS=$qos TOPIC_PATTERN_SUB="test/fanout/" RESTAPI=1 docker compose up -d sub
  sleep 5

  BROKER_HOST=$broker NUM_PUB=1 QOS=$qos PUB_INTERVAL=5 TOPIC_PATTERN_PUB="test/fanout/" docker compose up -d pub

  sleep $DURATION
  curl -s http://localhost:8080/metrics > "$BASE_OUTDIR/$broker/$tag/sub_metrics.log"
  docker logs sub > "$BASE_OUTDIR/$broker/$tag/sub_stdout.log" 2>&1

  docker compose down pub sub
  kill $stats_pid || true
}


mkdir -p "$BASE_OUTDIR"

for broker in "${BROKERS[@]}"; do
  echo "=============================="
  echo ">>> Benchmark broker: $broker"
  echo "=============================="
  
  
  mkdir -p "$BASE_OUTDIR/$broker"

  # --- Test P2P QoS 0 1 2 ---
  for qos in 0 1 2; do
    start_broker $broker
    run_p2p $broker $qos
    stop_all
  done
  
  start_broker $broker
  run_fanin $broker 1
  stop_all
  
  start_broker $broker
  run_fanout $broker 1
  stop_all

done

echo ">>> Benchmark completati"

