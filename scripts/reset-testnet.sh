#!/bin/bash
SCRIPT_DIR=$(cd -- "$(dirname -- "$0")" && pwd)
cd $SCRIPT_DIR/..
mkdir -p log
docker compose down
docker volume rm blockchain-hpc_pg_data
docker compose up >& log/blockchain.log &
sleep 60
$SCRIPT_DIR/populate-cl.sh
