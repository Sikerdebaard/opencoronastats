#!/bin/bash
. ./activate 

pip install -r ./requirements.txt 

python scripts/generate_data.py &
python scripts/hospitalized.py &
python scripts/covidwatchnl.py &
python scripts/case-counts.py &
python scripts/nursing_homes.py &
wait

python scripts/cards.py &
scripts/monkeypatch-lcps.py &
wait

python scripts/build.py 
