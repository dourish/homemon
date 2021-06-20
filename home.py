#!/usr/bin/python3
#
# Unified access to various home monitoring systems. These used to
# be a bunch of different scripts and programs, but this is an easier
# way to manage them.
#
# Usage: home.py command [args ... ]
# Commands:
#   sample <stream> -- display immediate value for stream
#   log <stream> -- add current stream data to time-stampled database
#   summary <stream> -- get today's min, avg, max for stream
# Streams:
#    demand -- electricity demand via Rainforest Eagle
#    pool -- pool temperature via Ambient Weather cloud service
#    battery -- pool temperature sensor battery via Ambient Weather
#

import sys
import os
import time
import requests
from datetime import datetime

LOGHOST='secondpi.local:8080'

# Configuration data for Rainforest Eagle
CLOUD_ID = '001cf6'
INSTALL_CODE = '9b935193995a4b22'
#ADDRESS = '192.168.254.34' #optional if your platform can resove mDNS

# Configuration data for Ambient Weather
os.environ['AMBIENT_ENDPOINT']        = 'https://api.ambientweather.net/v1'
os.environ['AMBIENT_API_KEY']         = '4b64dfe186e04e6da431fe850cf17c8245e773f34da648ccaf7c351b757242b2'
os.environ['AMBIENT_APPLICATION_KEY'] = '2b19c1c5857040179f9cbda25e12d15de828525864bf4fd4bf428284fa71be62'

# Configuration details for local weather station
# This is kinda silly. Should just have the whole URL in one.
WEATHERURL = 'https://api.weather.gov/stations/'
WEATHERSTATION = 'KLGB'
WEATHERDETAILS = '/observations/latest'

# Configurations above must be set before these imports happen since
# the imports trigger initialization code that depends on them.
from uEagle import Eagle
from ambient_api.ambientapi import AmbientAPI


# Fetch electricity demand data
def getdemand():
    eagle = Eagle(CLOUD_ID, INSTALL_CODE)
    demand_data = eagle.get_instantaneous_demand()
    return(demand_data['InstantaneousDemand']['Demand'])

# Fetch pool temperature data
def getpooltemp():
    ambient = AmbientAPI()
    devices = ambient.get_devices()
    device = devices[0]             # I only have one device

    time.sleep(1) #pause for a second to avoid API limits
    pool_data = device.get_data()
    return(pool_data[0]['tempf'])
    
# Fetch pool battery data
def getpoolbattery():
    ambient = AmbientAPI()
    devices = ambient.get_devices()
    device = devices[0]             # I only have one device

    time.sleep(1) #pause for a second to avoid API limits
    pool_data = device.get_data()
    return(pool_data[0]['battout'])

# Fetch current outdoor temperature
def getoutdoortemp():
    url = WEATHERURL + WEATHERSTATION + WEATHERDETAILS
    try:
        r = requests.get(url = url)
        rj = r.json()
        props = rj['properties']
        temp = props['temperature']
        vc = temp['value']
        vf = vc * 1.8 + 32
        return vf
    except Exception as e:
        print(e);
    

# Generic data lookup entry-point. This should probably use a parameter
# but instead looks at the command line parameters directly.
def getdata():
    if len(sys.argv) != 3:
        print("Usage: home.py sample stream")
        exit(1)
    if sys.argv[2] == "demand":
        data = getdemand()
        return(data)
    elif sys.argv[2] == "pool":
        data = getpooltemp()
        return(data)
    elif sys.argv[2] == "battery":
        data = getpoolbattery()
        return(data)
    elif sys.argv[2] == "klgb":
        data = getoutdoortemp()
        return(data)
    else:
        print("Unknown stream " + sys.argv[2])
        exit(1)

# Log a data item for the named stream (with timestamp).
def logdata(stream, data):
    params = {
        'data': data
    }
    url = 'http://' + LOGHOST + '/' + stream
    try:
        r = requests.post(url=url, params=params);
    except Exception as e:
        print(e);
        now = datetime.now()
        timestr = time.strftime("%Y-%m-%d %H:%M:%S");
        print(timestr + ": POST failed: " + url);

#
# TO DO: unify min/max/avg via a generic call (right now, code varies
# by just three characters across the three functions
#

# Look up the minimum value for the named stream (returns last 24hr).
def getmin(stream):
    params = {
        'stream': stream
    }
    url = 'http://' + LOGHOST + '/min'
    try:
        r = requests.get(url = url, params = params)
        rj = r.json();
        return rj;
    except Exception as e:
        print(e);
        now = datetime.now()
        timestr = time.strftime("%Y-%m-%d %H:%M:%S");
        print(timestr + ": GET failed: " + url);
        
# Look up the average value for the named stream (returns last 24hr).
def getavg(stream):
    params = {
        'stream': stream
    }
    url = 'http://' + LOGHOST + '/avg'
    try:
        r = requests.get(url = url, params = params)
        rj = r.json();
        return(rj['AVG(data)']);
    except Exception as e:
        print(e);
        now = datetime.now()
        timestr = time.strftime("%Y-%m-%d %H:%M:%S");
        print(timestr + ": GET failed: " + url);
        
# Look up the maximum value for the named stream (returns last 24hr).
def getmax(stream):
    params = {
        'stream': stream
    }
    url = 'http://' + LOGHOST + '/max'
    try:
        r = requests.get(url = url, params = params)
        return r.json();
    except Exception as e:
        print(e);
        now = datetime.now()
        timestr = time.strftime("%Y-%m-%d %H:%M:%S");
        print(timestr + ": GET failed: " + url);

# Look up the latest value for the named stream.
def getlatest(stream):
    params = {
        'stream': stream
    }
    url = 'http://' + LOGHOST + '/latest'
    try:
        r = requests.get(url = url, params = params)
        rj = r.json();
        return rj
    except Exception as e:
        print(e);
        now = datetime.now()
        timestr = time.strftime("%Y-%m-%d %H:%M:%S");
        print(timestr + ": GET failed: " + url);

# convenience functions to decode JSON
def getmaxdata(stream):
    return getmax(stream)['MAX(data)']
def getmaxtime(stream):
    return getmax(stream)['time']
def getmindata(stream):
    return getmin(stream)['MIN(data)']
def getmintime(stream):
    return getmin(stream)['time']


# Generic entry-point for data sampling
def do_sample():
    data = getdata()
    print(data)

# Generic entry-point for data logging
def do_log():
    data=getdata()
    logdata(sys.argv[2], data)

# Generic entry-point for data summary
def do_summary():
    stream = sys.argv[2];
    pmin=float(getmindata(stream))
    pavg=float(getavg(stream))
    pmax=float(getmaxdata(stream))
    plate=getlatest(stream)['data']
    #print("min = ", pmin, ", avg = ", pavg, ", max = ",  pmax)
    print("min = %0.3f, avg = %0.3f, max = %0.3f, latest=%0.3f"%(pmin, pavg, pmax, plate))

def do_latest():
    stream = sys.argv[2];
    r = getlatest(stream);
    print(r['data'], 'at', r['time'])

def do_max():
    stream = sys.argv[2];
    r = getmax(stream);
    print(r['MAX(data)'], 'at', r['time'])

def do_status():
    url = "http://" + LOGHOST + "/status"
    try:
        r = requests.get(url = url);
        rj = r.json();
        print (rj['COUNT(*)'], "entries in last 24 hours")
    except Exception as e:
        print(e);
        now = datetime.now()
        timestr = time.strftime("%Y-%m-%d %H:%M:%S");
        print(timestr + ": GET failed: " + url);
        

#
# Main entry point here
#

if len(sys.argv) < 2:
    print("Usage: home.py command args...")
    exit(1)

cmd = sys.argv[1]

if cmd=="sample":
    do_sample()
elif cmd=="log":
    do_log()
elif cmd=="summary":
    do_summary()
elif cmd=="status":
    do_status()
elif cmd=="latest":
    do_latest()
elif cmd=="max":
    do_max()
else:
    print(cmd + ": unrecognized command")
    exit(1)

    
