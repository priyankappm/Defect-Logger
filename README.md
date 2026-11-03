# Inspection Defect Logger

A small command-line tool for factory quality inspections. You start an inspection with a batch ID and sample size, record defects (critical / major / minor), list them, and get an ACCEPT or REJECT verdict recomputed from the defects so far, using the acceptance-limit table from the brief. State is kept in a local JSON file.

## Requirements
Python 3.8+ (standard library only, nothing to install).

## Install
```
git clone <your-repo-url>
cd inspection-defect-logger
```

## Run
```
python3 cli.py start --batch B-1001 --sample-size 50
python3 cli.py record --severity major --description "Cracked housing"
python3 cli.py list
python3 cli.py verdict
```
Use `--file path.json` (before the command) to keep state somewhere other than `inspection.json`. Invalid input prints an `Error:` message and exits with code 1.

## Run the tests
```
python3 -m unittest -v
```

## Time spent
About X hours. <-- fill in honestly

## AI session
<paste your shared Claude/ChatGPT link here>
