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

## CR-20260130-1153
Date: 2026-01-30 11:53
Source: chat

Request (verbatim):
update the ralphdocs to we are all matched up and decisions are logged

Notes:
- This request is to bring the RALPH docs (PRD/spec/tasks/progress) into alignment with the current repo behavior, including newer CLI options and extraction/recreation behavior added after CR-20260129-1210.

## CR-20260130-1210
Date: 2026-01-30 12:10
Source: chat

Request (verbatim):
update the code so I can use a specific json file in the path for the recreate
THE EXTRACT IS MISSING SLIDE 1-8 <pptx_path redacted>
validate yourself that it was fixed by running my script yourself
NOE recreate it with a new name
have all changed been checked into git ?
is gitignore including the correct items?
do not track any of the test json files like you mentioned vm_walking_deck/Vendor_Management_Roadmap_Current_info.json
make sure these folders are ingored as well __pycache__
review the README.md is accurate for all of the changes
run a code comparing the code to the docs/spec is there a mismatch?
yes update the ralphdocs to we are all matched up and decisions are logged

Notes:
- The “missing slide 1-8” report refers to verifying the extracted JSON contains a complete, ordered slide list for the REI deck.
