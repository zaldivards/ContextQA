<p  align="center">
   <img src="static/logo.png" width="200px" alt="SuperAGI logo" />
</p>
<p  align="center">
   <img src="static/title.png" width="200px" alt="SuperAGI logo" />
</p>

<p align="center" style="font-size: 20px">Chat with your documents by leveraging the power of LLMs and vector databases</p>

## 📽 Demo Video

https://github.com/zaldivards/ContextQA/assets/32210667/8e9a888a-504b-4470-bafe-8bbdc0a14dd2

## ⚙️ Setting up

---

#### 1. Clone the repository:

```bash
git clone https://github.com/zaldivards/contextqa.git && cd contextqa
```

#### 2. Install [docker](https://docs.docker.com/engine/install/)

#### 3. Set the following envs in the `contextqa.env` file

##### Required
- `OPENAI_API_KEY`: OpenAI api key
##### Optional
- `SQLITE_URL`: The SQLite URL to connect, it has a default value
- `LOCAL_VECTORDB_HOME`: ChromaDB home directory, it has a default value
- `DEPLOYMENT`: Environment name, default: dev
##### Additional configuration for connecting to an external MySQL database
Note that when setting the following envs SQLite will be ignored and MySQL will be used instead:
- `MYSQL_USER`: MySQL username
- `MYSQL_PASSWORD`: MySQL password
- `MYSQL_HOST`: MySQL host
- `MYSQL_DBNAME`: MySQL database name
- `MYSQL_EXTRA_ARGS`: Extra arguments after the connection string, i.e. **?somearg1=somevalue1&somearg2=somevalue2**
##### Additional configuration for supporting Pinecone
- `PINECONE_TOKEN`
- `PINECONE_INDEX`
- `PINECONE_ENVIRONMENT_REGION`

**Note**: Relational databases are used to control the digests of sources. Migrations will run automatically at the first startup.

### How to get the tokens?

| Keys           | Accesing the keys                                                                                                                                                                                                                                                                                                                                                                 |
| ---------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| OPENAI_API_KEY | First, you need to create an account [here](https://auth0.openai.com/u/signup/identifier?state=hKFo2SBMLTJkWUFpa2dVWlBrTDdrTjdxbEp2ZGt6RmZBakdvbKFur3VuaXZlcnNhbC1sb2dpbqN0aWTZIEhleHE1SGYzQkdpMjhDM3d3dnFVZERmamF6TVpTMEpGo2NpZNkgRFJpdnNubTJNdTQyVDNLT3BxZHR3QjNOWXZpSFl6d0Q). Then, you can generate and get the api key [here](https://platform.openai.com/account/api-keys) |
| PINECONE_TOKEN | Create an account [here](https://www.pinecone.io/). Then, you can generate and get the api key in the **API keys** section                                                                                                                                                                                                                                                                   |

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
