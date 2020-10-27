#!/bin/bash
. ./activate 

pip install -r ./requirements.txt 

python scripts/generate_data.py &
python scripts/hospitalized.py &
python scripts/covidwatchnl.py &
python scripts/outbreakmonitor.py &
python scripts/excessmortality.py &
python scripts/mobility.py &
python scripts/births.py &
python scripts/build.py &
wait

python scripts/cards.py 
