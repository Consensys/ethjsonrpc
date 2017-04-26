#!/bin/sh

set -e

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
LOG="$DIR"/geth.log
PID="$DIR"/geth.pid
IPC="$DIR"/geth.ipc

start() {
  if [ ! -e "$PID" ]; then
    geth --dev --rpc --datadir "$DIR" "$IPC" 2> "$LOG" &
    echo $! > "$PID" && \
    until $(curl --output /dev/null --silent --head --fail http://127.0.0.1:8545); do
      sleep 1
    done
    geth --datadir "$DIR" --exec 'loadScript("'"$DIR"'/setup.js"); console.log(miner)' attach "$IPC"
  fi
}

stop() {
  if [ -e "$PID" ]; then
    kill $(cat "$PID")
    rm "$PID"
  fi
}

if [ "$1" = "start" ]; then
  start
elif [ "$1" = "stop" ]; then
  stop
elif [ "$1" = "clean" ]; then
  rm -f "$PID" "$LOG" "$IPC"
fi


