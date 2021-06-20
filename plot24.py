#!/usr/bin/python3
#
# Plot last 24 hours of stream data
#

import pandas as pd
import plotly.express as px
import sys

ranges = {
    'pool': [60.0,90.0],
    'demand': [0,5]
};

if len(sys.argv) != 2:
    print('Usage: plot24 stream')
    exit(1)
    

stream=sys.argv[1]

# if we don't specify a day, or start/end parameters, default will be
# last 24 hours.
url = "http://secondpi.local:8080/data?stream="+stream

df = pd.read_json(url);

ry = ranges[stream]
fig = px.line(df['data'], range_y=ry)
fig.show()

