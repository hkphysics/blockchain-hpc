#!/bin/bash

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd $SCRIPT_DIR/..
. $SCRIPT_DIR/local-addresses.sh
STATE_FILE=./state/state.json

# Define a function to clean up and kill all children
cleanup_and_exit() {
    echo "Interrupted. Killing all child processes."
    pgrep -P $$ | xargs kill
}

if [ -s $STATE_FILE ]; then
    echo "node started with state file...."
    /root/.foundry/bin/anvil --host 0.0.0.0 --load-state $STATE_FILE --dump-state $STATE_FILE &
else
    /root/.foundry/bin/anvil --host 0.0.0.0 --dump-state $STATE_FILE &
    echo "node started waiting...."
    sleep 3
    (npx hardhat --network localhost run ./scripts/deploy-token.ts)
    (npx hardhat --network localhost run ./scripts/deploy-operator.ts)
    (npx hardhat --network localhost run ./scripts/deploy-example.ts)
    (npx hardhat --network localhost run ./scripts/deploy-validator.ts)
fi

# Trap interrupts and call our cleanup function
trap "cleanup_and_exit" INT  # Ctrl+C

sleep infinity

