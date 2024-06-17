<p  align="center">
   <img src="static/logo.png" width="200px" alt="SuperAGI logo" />
</p>
<p  align="center">
   <img src="static/title.png" width="200px" alt="SuperAGI logo" />
</p>

<p align="center" style="font-size: 20px">Chat with your data by leveraging the power of LLMs and vector databases</p>

## 📽 Demo Video

https://github.com/zaldivards/ContextQA/assets/32210667/8e9a888a-504b-4470-bafe-8bbdc0a14dd2

## ⚙️ Setting up

---

#### 1. Clone the repository:

```bash
git clone https://github.com/zaldivards/contextqa.git && cd contextqa
```

#### 2. Install [docker](https://docs.docker.com/engine/install/)

#### 3. Set the following envs in the `contextqa.env` file - **OPTIONAL**

1. **CONFIG_PATH**:
   - Example: **`path/to/settings-file.json`**
   - Usage: Specifies the path to the configuration file. It **must** be a json file
   - Default: **`settings.json`**
2. **MEDIA_HOME**:
   - Example: **`path/to/some-dir`**
   - Usage: Specifies the path to the directory that will hold ingested PDFs
   - Default: **`.media`**
3. **SQLITE_URL**:
   - Example: **`sqlite://path/to/database.sqlite3`**
   - Usage: Specifies the SQLite database connection
   - Default: **`sqlite:///contextqa.sqlite3`**
4. **LOCAL_VECTORDB_HOME**:
   - Example: **`path/to/some-dir`**
   - Usage: Home directory of ChromaDB
   - Default: **`.chromadb`**
5. **DEPLOYMENT**:
   - Example: **`dev`**
   - Usage: Environment name
   - Default: **`dev`**

**Note**: Relational databases are used to control the digests of sources. Migrations will run automatically at the first startup.

### How to get the tokens?

| Keys           | Accesing the keys                                                                                                                                                                                                                                                                                                                                                                |
| -------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| OPENAI_API_KEY | First, you need to create an account [here](https://auth0.openai.com/u/signup/identifier?state=hKFo2SBMLTJkWUFpa2dVWlBrTDdrTjdxbEp2ZGt6RmZBakdvbKFur3VuaXZlcnNhbC1sb2dpbqN0aWTZIEhleHE1SGYzQkdpMjhDM3d3dnFVZERmamF6TVpTMEpGo2NpZNkgRFJpdnNubTJNdTQyVDNLT3BxZHR3QjNOWXZpSFl6d0Q). Then, you can generate and get the api key [here](https://platform.openai.com/account/api-keys) |
| PINECONE_TOKEN | Create an account [here](https://www.pinecone.io/). Then, you can generate and get the api key in the **API keys** section                                                                                                                                                                                                                                                       |

## 💻 Usage

---

```bash
bash run.sh [start|restart|shutdown] [dev|prod] OPTIONS
```

### Starting the development or production environment for the first time

```bash
bash run.sh start dev
```

or

```bash
bash run.sh start prod
```

### Other examples

```bash
bash run.sh start dev --build
```

```bash
bash run.sh restart dev --strict
```

```bash
bash run.sh shutdown dev
```

**Note**: You can display the usage message with the `--help` flag:

```bash
bash run.sh [start|restart|shutdown] --help
```
