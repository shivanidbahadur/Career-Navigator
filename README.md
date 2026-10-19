# Career-Navigator

AI Career Navigator — a Streamlit app that recommends careers, finds skill gaps,
builds a learning roadmap, matches jobs, generates a resume and runs a mock
interview scored by Claude.

## Run locally

```bash
python -m venv venv
venv/Scripts/activate        # Windows
# source venv/bin/activate   # macOS / Linux
pip install -r requirements.txt
streamlit run app.py
```

The app opens on <http://localhost:8501>. Accounts and progress live in
`data/app.db` (SQLite); delete that file to start fresh — it is recreated on
first run.

The mock interview calls the Anthropic API. Provide a key either as an
environment variable or in `.streamlit/secrets.toml`:

```toml
# .streamlit/secrets.toml  (never commit this file)
ANTHROPIC_API_KEY = "sk-ant-..."
```

Without a key the interview still runs and falls back to generic feedback.

## Deploy

`render.yaml` is a [Render Blueprint](https://render.com/docs/blueprint-spec):

1. Push to GitHub, then in Render choose **New → Blueprint** and pick this repo.
2. Render reads `render.yaml`, installs `requirements.txt` and starts
   `streamlit run app.py` on the assigned port.
3. Paste your `ANTHROPIC_API_KEY` when prompted for the secret.

The deployed app runs against `var/app.db` rather than the committed
`data/app.db`, so it starts with an empty database. Hosts that read a
`Procfile` (Railway, Heroku) can use the same start command from that file.
