startUsage="Usage: bash run.sh start ENV [OPTIONS]
  
  Start ContextQA server and client

Arguments:
  ENV [dev|prod]  The environment name [required]

Options:
  --help    Show this message
  --build   Flag to build and start the server and client
"

restartUsage="Usage: bash run.sh restart ENV [OPTIONS]
  
  Restart ContextQA server and client

Arguments:
  ENV [dev|prod]  The environment name [required]

Options:
  --help           Show this message
  --strict         Restart ContextQA server and client after building
  --from-scratch   Restart ContextQA server and client after a clean build with no cache 
"


if command -v docker-compose > /dev/null 2>&1; then
    compose="docker-compose"
elif command -v docker compose > /dev/null 2>&1; then
    compose="docker compose"
else
    echo "Please install docker and docker-compose to continue, more information here: https://docs.docker.com/engine/install/"
    exit
fi

echo "Setting /var/contextqa/embeddings as the local vector store"
if [ ! -d /var/contextqa/embeddings ]; then
    sudo mkdir -p /var/contextqa/embeddings
fi
export VECTOR_STORE_HOME="/var/contextqa/embeddings"

start(){
    if [ "$1" == "--help" ]; then
        echo "$startUsage"
        exit
    fi
    echo -e '\n::::: Starting ContextQA :::::\n'
    env=$1
    shift
    $compose -f "docker-compose-$env.yml" up "$@"
}

restart(){
    if [ "$1" == "--help" ]; then
        echo "$restartUsage"
        exit
    fi
    echo -e '\n::::: Restarting ContextQA :::::\n'
    if [ "$2" == "--from-scratch" ]; then
        $compose -f "docker-compose-$1.yml" down
        $compose -f "docker-compose-$1.yml" build --no-cache
        $compose -f "docker-compose-$1.yml" up 
    elif [ "$2" == "--strict" ]; then
        start $1 --build
    else
        $compose -f "docker-compose-$1.yml" restart
    fi
}

"$@"