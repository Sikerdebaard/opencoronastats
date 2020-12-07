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
python scripts/nursing_homes.py &
python scripts/ggd-tests-performed.py &
wait

python scripts/healthcare-workers.py &
python scripts/agedistributions.py &
python scripts/outbreakmonitor.py &
python scripts/excessmortality.py &
python scripts/monkeypatch-lcps.py &
wait

cp data/testing-per-group.csv html/
python scripts/cards.py 
python scripts/build.py 
