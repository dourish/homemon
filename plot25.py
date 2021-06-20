#!/usr/bin/python3

import urllib
import pandas as pd
import sqlite3 as sql
import plotly.express as px
import sys

ranges = {
    'pool': [60.0,90.0],
    'demand': [0,5]
};

if len(sys.argv) == 1:
    print('Usage: plot25 stream date (e.g. "pool 2021-06-18")')
    exit(1)
    

stream=sys.argv[1]
day=sys.argv[2]

url = "http://secondpi.local:8080/data?stream="+stream+"&day="+day

df = pd.read_json(url);

ry = ranges[stream]
fig = px.line(df['data'], range_y=ry)
fig.show()

