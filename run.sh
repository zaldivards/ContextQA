current_path="$( cd -- "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"

local(){
    python app.py "$@"
}

build-docker(){
    echo "..:: build-docker ::.."
    docker build -t llm-retriever $current_path
}

dockerized(){
    if [ "$1" == "--build" ]; then
        build-docker
    fi
    docker run --rm -v $current_path:/app llm-retriever python app.py "$@"
}

"$@"