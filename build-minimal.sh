#!/bin/bash
. ./activate 

pip install -r ./requirements.txt 

python scripts/vaccine-demographics.py &
python scripts/vaccine.py &
python scripts/generate_data.py &
python scripts/hospitalized.py &
python scripts/covidwatchnl.py &
python scripts/case-counts.py &
python scripts/nursing_homes.py &
python scripts/mortality-displacement.py &
wait

python scripts/cards.py &
python scripts/monkeypatch-lcps.py &
wait

cp data/testing-per-group.csv html/
python scripts/build.py 
