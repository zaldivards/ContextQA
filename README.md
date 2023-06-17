# LLM data retriever

Basic project powered by LLMs to retrieve certain information

## Setup

1. Install docker
2. Set the following envs in a `.env` file

   - OPENAI_API_KEY
   - SERPAPI_API_KEY
   - TWITTER_API_KEY
   - TWITTER_API_SECRET
   - TWITTER_ACCESS_TOKEN
   - TWITTER_ACCESS_SECRET

## Usage

```bash
bash run.sh dockerized [--build]
```

You should use the `--build` flag when it is the first execution or you want to rebuild the docker image
