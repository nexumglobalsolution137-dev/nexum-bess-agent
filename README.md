---
title: Nexum BESS AI Operations Agent
emoji: 🔋
colorFrom: blue
colorTo: green
sdk: gradio
app_file: app.py
pinned: false
---

# Nexum BESS AI Operations Agent

A deployable **simulation-only** multi-agent Battery Energy Storage System (BESS) demonstration by Nexum Global Solution.

## Features
- Solar/load forecasting using transparent synthetic 24-hour profiles
- Heuristic battery dispatch optimization with state-of-charge and power constraints
- Battery diagnostics and safety warnings
- Digital twin with energy flow and SoC charts
- Supervisor decision summary and KPI dashboard

## Run locally
```bash
python -m pip install -r requirements.txt
python app.py
```

## Hugging Face Spaces
1. Create a new **Gradio** Space.
2. Upload the files in this repository to the Space root (including this README).
3. Wait for the Space to build; no API key is required.

## GitHub
Create a repository and push these files:
```bash
git init
git add .
git commit -m "Initial BESS agent demo"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/nexum-bess-agent.git
git push -u origin main
```

## Important safety limitations
**Not for connection to a real battery, PCS, BMS, EMS, or grid.** This application is a deterministic educational simulator with heuristic scheduling, not an LLM-powered autonomous controller or validated optimization engine. The simulated operating constraints are simplified. Actual deployments require approved equipment integrations, real-time interlocks, certified protection, cybersecurity controls, engineering validation, and human oversight. The app never issues hardware commands.

## Architecture
`Synthetic forecasts → Dispatch planner → Simulated BESS → Diagnostics → Supervisor report + Gradio dashboard`
