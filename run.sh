current_path="$( cd -- "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
command_="uvicorn main:app --host 0.0.0.0 --port 8080 --reload"


check-envs(){
    if [ -f "$current_path/.env" ]; then
        echo ".env file found, loading environment variables"
        export `cat $current_path/.env | xargs`
    else
        echo ".env file not found, stopping initialization"
        exit 1
    fi
}

local(){
    check-envs
    exec $command_
}

build-docker(){
    echo "..:: build-docker ::.."
    docker build -t llm-retriever $current_path
}

dockerized(){
    if [ "$1" == "--build" ]; then
        build-docker
    fi
    check-envs
    docker run --env-file $current_path/.env --rm  -p 8080:8080 -v $current_path:/app llm-retriever $command_
}

"$@"