<p  align="center">
   <img src="static/logo.png" width="200px" alt="SuperAGI logo" />
</p>
<p  align="center">
   <img src="static/title.png" width="200px" alt="SuperAGI logo" />
</p>

<p align="center" style="font-size: 20px">Open-source utility to query documents by leveraging the power of LLMs and vector databases</p>

## ⚙️ Setting up

---

1. Install docker
2. Set the following envs in a `.env` file in the `api` root

   - OPENAI_API_KEY  **(required)**
   - SERPAPI_API_KEY
   - TWITTER_API_KEY
   - TWITTER_API_SECRET
   - TWITTER_ACCESS_TOKEN
   - TWITTER_ACCESS_SECRET

## 💻 Usage

---

```bash
bash run.sh [start|restart] [dev|prod] OPTIONS
```

You can display the usage message with the `--help` flag, for instance:

```bash
bash run.sh start --help
```

or

```bash
bash run.sh restart --help
```

### Examples

```bash
- bash run.sh start dev --build
- bash run.sh restart dev --strict
```
