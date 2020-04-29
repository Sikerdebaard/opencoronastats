#!/bin/bash
. ./activate && pip install -r ./requirements.txt && python scripts/generate_data.py && python scripts/covidwatchnl.py && python scripts/excessmortality.py && python scripts/mobility.py && python scripts/cards.py && python scripts/build.py
