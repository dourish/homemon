#!/usr/bin/python3
#
# Produce a weekly summary.

import time
from datetime import date
import requests
import json
import sys

if (len(sys.argv) != 2):
    print("Usage: weekly.py stream")
    exit(1)
    
stream = sys.argv[1]

dayNames = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

# truncate to two decimal places. this is truly silly but since
# formatted output isn't really a Python thing, here we are.
def to2dec(n):
    return(int(n * 100) / 100.0)

# what is today's date?
now = time.time()

# make a list of the last seven days
days=[]
for x in range(7):
    days.append(now - (7-x)*60*60*24)

# now print the days of the week for each of those times (testing)
#for d in days:
#    date1 = date.fromtimestamp(d)
#    print(dayNames[date1.weekday()])

# variables for running totals
wtotal = 0
wmin = 0
wmax = 0

# for each day, get min/avg/max, print and update running counts
for d in days:
    date1 = date.fromtimestamp(d)
    isodate = date1.isoformat();

    # I should really have all these calls wrapped in an exception handler
    url1 = "http://secondpi.local:8080/avg?stream="+stream+"&day=" + isodate
    r = requests.get(url1);
    rj = r.json();
    avg = rj['AVG(data)']
    url1 = "http://secondpi.local:8080/min?stream="+stream+"&day=" + isodate
    r = requests.get(url1);
    rj = r.json();
    min = rj['MIN(data)']
    url1 = "http://secondpi.local:8080/max?stream="+stream+"&day=" + isodate
    r = requests.get(url1);
    rj = r.json();
    max = rj['MAX(data)']

    print(dayNames[date1.weekday()]+":", min, to2dec(avg), max);

    wtotal += avg
    if (max > wmax):
        wmax = max
    if (min < wmin) or (wmin == 0):
        wmin = min


print("Weekly: ", wmin, to2dec(wtotal/7.0), wmax)

    
