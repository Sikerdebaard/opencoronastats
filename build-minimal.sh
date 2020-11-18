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
python scripts/monkeypatch-lcps.py &
wait

cp data/testing-per-group.csv html/
python scripts/build.py 
