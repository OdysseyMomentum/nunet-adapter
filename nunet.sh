if [[ "$1" == "local" ]]; then
    if [[ "$2" == "up" ]]; then
        docker-compose -f docker-compose.all.yml up --force-recreate  local_nunet
    elif [[ "$2" == "build" ]]; then
        docker-compose -f docker-compose.all.yml build  local_nunet
    elif [[ "$2" == "stop" ]]; then
        docker-compose -f docker-compose.all.yml stop local_proxy local_nunet local_webapp
    else
        echo "command local can only be used with up, build or stop"
    fi
elif [[ "$1" == "localnp" ]]; then
    if [[ "$2" == "up" ]]; then
        docker rm -f local_proxy local_nunet_no_persist local_webapp
        docker-compose -f docker-compose.all.yml up --force-recreate --build local_proxy local_nunet_no_persist local_webapp
    elif [[ "$2" == "build" ]]; then
        docker-compose -f docker-compose.all.yml build local_proxy local_nunet_no_persist local_webapp
    elif [[ "$2" == "stop" ]]; then
        docker-compose -f docker-compose.all.yml stop local_proxy local_nunet_no_persist local_webapp
    else
        echo "command test can only be used with up, build or stop"
    fi
else
    echo "available commands: production, dev, test, local, localnp"
fi
