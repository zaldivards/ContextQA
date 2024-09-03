<p  align="center"><a href="https://pypi.org/project/contextqa"><img src="https://contextqa-assets.s3.amazonaws.com/logo.png" width="200px" alt="ContextQA logo" /></a></p>
<p  align="center"><a href="https://pypi.org/project/contextqa"><img src="https://contextqa-assets.s3.amazonaws.com/title.png" width="200px" alt="ContextQA title" /></a></p>
<p align="center" style="font-size: 20px"><i>Chat with your data by leveraging the power of LLMs and vector databases</i></p>
<p align="center">
<a href="https://pypi.org/project/contextqa" target="_blank">
    <img alt="contextqa latest version" src="https://img.shields.io/pypi/v/contextqa?label=Latest%20release&color=%230cc109">
</a>
<a href="https://pypi.org/project/contextqa" target="_blank">
   <img alt="Supported Python versions" src="https://img.shields.io/pypi/pyversions/contextqa?logo=python&logoColor=white&color=0cc109">
</a>
<img alt="node version" src="https://img.shields.io/badge/nodejs-v18.17.1-green?logo=nodedotjs">
<img alt="vue version" src="https://img.shields.io/badge/Vue.js-%5Ev3.2.13-green?logo=vuedotjs">
</p>

---

ContextQA is a modern utility that provides a ready-to-use LLM-powered application. It is built on top of giants such as [FastAPI](https://fastapi.tiangolo.com/), [LangChain](https://www.langchain.com/), and [Hugging Face](https://huggingface.co/).

Key features include:
- Regular chat supporting knowledge expansion via internet access
- Conversational QA with relevant sources
- Streaming responses
- Ingestion of data sources used in QA sessions
- Data sources management
- LLM settings: Configure parameters such as provider, model, temperature, etc. Currently, the supported providers are **[OpenAI](https://openai.com/)** and **Google** 
- Vector DB settings. Adjust parameters such as engine, chunk size, chunk overlap, etc. Currently, the supported engines are **[ChromaDB](https://www.trychroma.com/)** and **[Pinecone](https://www.pinecone.io/)**
- Other settings: Choose embedded or external LLM memory (**[Redis](https://redis.io/)**), media directory, database credentials, etc.


## Installation

```bash
pip install contextqa
```
## Usage
On installation contextqa provides a CLI tool 
```bash
contextqa init
```
Check out the available parameters by running the following command
```bash
contextqa init --help
```
## Example
### Run it
```bash
$ contextqa init

2024-08-28 01:00:39,586 - INFO - Using SQLite
2024-08-28 01:00:47,850 - INFO - Use pytorch device_name: cpu
2024-08-28 01:00:47,850 - INFO - Load pretrained SentenceTransformer: sentence-transformers/all-mpnet-base-v2
INFO:     Started server process [20658]
INFO:     Waiting for application startup.
2024-08-28 01:00:47,850 - INFO - Running initial migrations...
2024-08-28 01:00:47,853 - INFO - Context impl SQLiteImpl.
2024-08-28 01:00:47,855 - INFO - Will assume non-transactional DDL.
2024-08-28 01:00:47,860 - INFO - Running upgrade  -> 0bb7d192c063, Initial migration
2024-08-28 01:00:47,862 - INFO - Running upgrade 0bb7d192c063 -> b7d862d599fe, Support for store types and related indexes
2024-08-28 01:00:47,864 - INFO - Running upgrade b7d862d599fe -> 3058bf204a05, unique index name
INFO:     Application startup complete.
INFO:     Uvicorn running on http://localhost:8080 (Press CTRL+C to quit)
```
### Check it

Open your browser at http://localhost:8080. You will see the initialization stepper which will guide you through the initial configurations

<img alt="init config" src="https://contextqa-assets.s3.amazonaws.com/init.png" width="1000px">

Or the main contextqa view - If the initial configuration has already been set

<img alt="main view" src="https://contextqa-assets.s3.amazonaws.com/main.png" width="1000px">

## Guideline

For detailed usage instructions, please refer to the [usage guidelines](https://zaldivards.github.io/introducing-contextqa/).

## Contributing

We welcome contributions to **ContextQA**! To get started, please refer to our [CONTRIBUTING.md](CONTRIBUTING.md) file for guidelines on how to contribute. 
Your feedback and contributions help us improve and enhance the project. Thank you for your interest in contributing!