#!/bin/bash
. ./activate 

pip install -r ./requirements.txt 

python scripts/generate_data.py &
python scripts/hospitalized.py &
python scripts/covidwatchnl.py &
python scripts/mobility.py &
python scripts/births.py &
python scripts/case-counts.py &
python scripts/euromomo.py &
wait

python scripts/agedistributions.py
python scripts/outbreakmonitor.py &
python scripts/excessmortality.py &
python scripts/cards.py &
scripts/monkeypatch-lcps.py &
wait

python scripts/build.py 
