#/bin/bash

postgres_running () {
  service postgresql status | grep online
  return
}

start () {
  export PYTHONPATH=$PYTHONPATH:/usr/local/lib/python3/dist-packages
  echo "Starting services"
  service postgresql start && bash
  # Restart the services if they fail
  while sleep 15; do
    postgres_running
    if [ $? -ne 0 ]; then service postgresql restart; fi
  done
}

stop () {
  echo "Stopping services"
  service postgresql stop
}

trap_handler () {
  printf "\nThe trap handler has been fired with signal = $1 \n"
  stop
}

# For Ctrl + c
trap 'trap_handler SIGINT' SIGINT
# For docker stop
trap 'trap_handler SIGTERM' SIGTERM

CHILD=""
arg="$@"
if [ "$arg" == "start" ]; then
  start
elif [ "$arg" == "stop" ]; then
  stop
else
  eval $@ &
  CHILD=$!
  wait "$CHILD"
fi