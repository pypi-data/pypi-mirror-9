#!/usr/bin/env bash
sudo pkill -f handler 
DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )
sudo "$DIR/handler.sh" &
scratch --document "$DIR/default.sb"