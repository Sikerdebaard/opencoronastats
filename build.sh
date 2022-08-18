#!/bin/bash
. ./activate 

#pip install -r ./requirements.txt 
#
#python scripts/vaccine-demographics.py &
#python scripts/vaccine.py &
#python scripts/generate_data.py &
#python scripts/hospitalized.py &
#python scripts/covidwatchnl.py &
#python scripts/mobility.py &
#python scripts/births.py &
#python scripts/case-counts.py &
#python scripts/euromomo.py &
#python scripts/nursing_homes.py &
#python scripts/ggd-tests-performed.py &
#wait
#
#python scripts/healthcare-workers.py &
#python scripts/agedistributions.py &
##python scripts/outbreakmonitor.py &
##python scripts/excessmortality.py &
#python scripts/mortality-displacement.py &
#python scripts/monkeypatch-lcps.py &
#wait
#
#cp data/testing-per-group.csv html/
#python scripts/cards.py 
#python scripts/build.py 

`which time` -ao logs/log-pip pip install -r ./requirements.txt

`which time` -ao logs/log-qrcode python scripts/qrcode.py &
#`which time` -ao logs/log-qrcode python scripts/ecdc_vaccine.py &
`which time` -ao logs/log-generate_data python scripts/generate_data.py &
`which time` -ao logs/log-hospitalized python scripts/hospitalized.py &
`which time` -ao logs/log-covidwatchnl python scripts/covidwatchnl.py &
# `which time` -ao logs/log-mobility python scripts/mobility.py &   # mobility is broken
`which time` -ao logs/log-births python scripts/births.py &
`which time` -ao logs/log-case-counts python scripts/case-counts.py &
`which time` -ao logs/log-euromomo python scripts/euromomo.py &
`which time` -ao logs/log-nursing_homes python scripts/nursing_homes.py &
`which time` -ao logs/log-ggd-tests-performed python scripts/ggd-tests-performed.py &
wait

# `which time` -ao logs/log-healthcare-workers python scripts/healthcare-workers.py &  # disabled
`which time` -ao logs/log-agedistributions python scripts/agedistributions.py &
#python scripts/outbreakmonitor.py &
#python scripts/excessmortality.py &
#`which time` -ao logs/log-mortality-displacement python scripts/mortality-displacement.py &  # mortality displacement broken
#`which time` -ao logs/log-monkeypatch-lcps python scripts/monkeypatch-lcps.py &
wait

cp data/testing-per-group.csv html/
`which time` -ao logs/log-cards python scripts/cards.py
`which time` -ao logs/log-build python scripts/build.py

