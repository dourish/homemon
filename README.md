# homemon
Clients and server for simple home monitoring package

Simple client/server based home monitor, linked by REST APIs.

The server is a node.js program which uses an sqlite3 database to keep track of entries. Entries
are organized as "streams", each of which is a data stream from a particular sensor. Calls to
the server can be used to add entries, retreive data, and do some very basic summaries (e.g.
max, min, avg).

The clients are Python programs that use RESTful APIs to make calls on the server. The main
client is home.py, a command line tool for looking up data and adding log entries. Home.py
knows how to talk to the various sensors, which include National Weather Service temperature
monitors, a pool monitor using Ambient Weather's API, and a Rainforest Eagle electricity
demand monitor.

plotdays.py looks up data to produce graphs.
