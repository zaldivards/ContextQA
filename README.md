<p  style="display: flex;align-items: center;">
   <img src="static/logo.png" width="5%" alt="SuperAGI logo" />
   <span style="font-size: 40px; padding-left: 10px;">QueryMan</span>
</p>

<p style="font-size: 20px">Open-source utility to query documents by leveraging the power of LLMs and vector databases</p>

## ⚙️ Setting up
---

1. Install docker
2. Set the following envs in a `.env` file

   - OPENAI_API_KEY
   - SERPAPI_API_KEY
   - TWITTER_API_KEY
   - TWITTER_API_SECRET
   - TWITTER_ACCESS_TOKEN
   - TWITTER_ACCESS_SECRET

## 💻 Usage
---

```bash
bash run.sh dockerized [--build]
```

You should use the `--build` flag when it is the first execution or you want to rebuild the docker image
