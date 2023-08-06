#!/usr/bin/env bash

DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )
until python $DIR/handler.py; do
    echo "Disconnected from Scratch, respawning" >&2
    sleep 1
done