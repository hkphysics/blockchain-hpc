#!/bin/bash

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd $SCRIPT_DIR/..
source $SCRIPT_DIR/scripts/local-addresses.sh

# Define a function to clean up and kill all children
cleanup_and_exit() {
    echo "Interrupted. Killing all child processes."
    pgrep -P $$ | xargs kill
}

(npx hardhat node --hostname 0.0.0.0) &

echo "node started waiting...."
sleep 3
(npx hardhat --network localhost run ./scripts/deploy-token.ts)
(npx hardhat --network localhost run ./scripts/deploy-operator.ts)
(npx hardhat --network localhost run ./scripts/deploy-example.ts)

# Trap interrupts and call our cleanup function
trap "cleanup_and_exit" INT  # Ctrl+C

sleep infinity

