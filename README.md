# AI Investment Platform

Building AI-native investment workflow products as portfolio for career transition into hands-on AI Product Manager roles in finance and AI-native firms.

## Status

Under active development. See CONTEXT.md for current state.

## Modules

1. **Factor Research Copilot** - AI-assisted equity factor research
2. **Backtesting Copilot** - Natural-language strategy simulation
3. **Portfolio Construction Copilot** - AI-assisted portfolio optimization
4. **ML Signal Lab** - AI-assisted ML experimentation for financial signals

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # then add your API key
```

## Tech Stack

- Python 3.11 (managed via pyenv)
- Anthropic API (Claude Sonnet)
- pandas, numpy, scipy
- yfinance → Polygon.io
- FastAPI + Streamlit
- WSL2 Ubuntu 26.04 dev environment
