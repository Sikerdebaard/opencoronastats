#!/bin/bash
. ./activate
python scripts/generate_data.py
python scripts/covidwatchnl.py
python scripts/excessmortality.py
python scripts/build.py
