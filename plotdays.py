#!/usr/bin/python3
#
# Plot data from home data logging server. Plots multiple days on the
# same graph.
#
# Command line: ploydays.py <stream> <day> [<day>...]
#

import urllib
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sys

ranges = {
    'pool': [60.0,90.0],
    'demand': [0,5],
    'klgb': [30,120]
};

if len(sys.argv) == 1:
    print('Usage: plotdays stream date date* (e.g. "pool 2021-06-18")')
    exit(1)

stream=sys.argv[1]

# First, make a list of the days we want from the command line
days = []
for x in range(2, len(sys.argv)):
    days.append(sys.argv[x])

# Now fetch the daata for each of those days
frames = []
for d in days:
    url = "http://secondpi.local:8080/data?stream="+stream+"&day="+d
    df = pd.read_json(url)
    frames.append(df)

fig = go.Figure()

# add each data from to the figure
for x in range(0, len(days)):
    fig.add_trace(go.Scatter(y=frames[x]['data'], mode='lines', name=days[x]))

# Set ticks and tick text
fig.update_layout(
    xaxis = dict(
        tickmode = 'array',
        tickvals = [0, 12, 24, 36, 48, 60, 72, 84, 96, 108, 120, 132,
                    144, 156, 168, 180, 192, 204, 216, 228, 240, 252,
                    264, 276],
        ticktext = ['mid', '1am', '2am', '3am', '4am', '5am', '6am',
                    '7am', '8am', '9am', '10am', '11am', 'noon',
                    '1pm', '2pm', '3pm', '4pm', '5pm', '6pm', '7pm',
                    '8pm', '9pm', '10pm', '11pm']
    )
)

# Display the figure
fig.show()



