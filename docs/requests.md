# Customer Requests (append-only)

## CR-20260129-1210
Date: 2026-01-29 12:10
Source: chat

Request (verbatim):
$ralph create a run.sh that will did this  - python3.11 -m venv .venv (or python3 -m venv .venv if that’s not 3.14)
      - source .venv/bin/activate
      - python -m pip install -r requirements.txt and then start the app 
also update readme.md with the info about using ./run.sh

Notes:
- Repo is a CLI tool (not a long-running server); “start the app” is interpreted as “run the CLI entrypoint (main.py)”.
