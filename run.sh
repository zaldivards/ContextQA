current_path="$( cd -- "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
command_="uvicorn main:app --host 0.0.0.0 --port 8080 --reload"

local(){
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
    docker run --rm -p 8080:8080 -v $current_path:/app llm-retriever $command_
}

"$@"