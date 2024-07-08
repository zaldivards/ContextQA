startUsage="Usage: bash run.sh start [OPTIONS]
  
  Start ContextQA server and client

Options:
  --help    Show this message
  --build   Flag to build and start the server and client
"

restartUsage="Usage: bash run.sh restart [OPTIONS]
  
  Restart ContextQA server and client

Options:
  --help           Show this message
  --strict         Restart ContextQA server and client after building
  --from-scratch   Restart ContextQA server and client after a clean build with no cache 
"

shutdownUsage="Usage: bash run.sh shutdown
  
  Shutdown ContextQA server and client

Options:
  --help           Show this message
"


if command -v docker-compose > /dev/null 2>&1; then
    compose="docker-compose"
elif command -v docker compose > /dev/null 2>&1; then
    compose="docker compose"
else
    echo "Please install docker and docker-compose to continue, more information here: https://docs.docker.com/engine/install/"
    exit
fi

if [ ! -d /var/contextqa/embeddings ]; then
    echo "Setting /var/contextqa/embeddings as the local vector store"
    sudo mkdir -p /var/contextqa/embeddings
fi
export VECTOR_STORE_HOME="/var/contextqa/embeddings"

start(){
    if [ "$1" == "--help" ]; then
        echo "$startUsage"
        exit
    fi
    echo -e '\n::::: Starting ContextQA :::::\n'
    $compose -f "docker-compose.yml" up -d "$@"
}

restart(){
    if [ "$1" == "--help" ]; then
        echo "$restartUsage"
        exit
    fi
    echo -e '\n::::: Restarting ContextQA :::::\n'
    if [ "$1" == "--from-scratch" ]; then
        $compose -f "docker-compose.yml" down
        $compose -f "docker-compose.yml" build --no-cache
        $compose -f "docker-compose.yml" up -d
    elif [ "$1" == "--strict" ]; then
        start --build
    else
        $compose -f "docker-compose.yml" restart
    fi
}

shutdown(){
  if [ "$1" == "--help" ]; then
    echo "$shutdownUsage"
    exit
  fi
  $compose -f "docker-compose.yml" down
}

"$@"