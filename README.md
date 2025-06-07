# Article Rewriter

This project hosts a small Streamlit application for rewriting and translating articles with the help of LLM APIs.

## Structure

- `app.py` &ndash; main Streamlit application
- `rewriter/` &ndash; package containing API helper code
- `.devcontainer/` &ndash; configuration for running inside a dev container

## Running locally

Install dependencies then launch Streamlit:

```bash
pip install -r requirements.txt
streamlit run app.py
```

Secrets such as `OPENAI_KEY` and `ANTHROPIC_KEY` need to be provided via `streamlit.secrets`.
