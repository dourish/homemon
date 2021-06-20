//
// Simple RESTFUL server for home data logging. This is my second
// version, rewritten using express.js since it has better facilities
// for letting me return the results of SQL queries, which I need for
// graphing data.
//
// Paul Dourish, June 2021
//

var express = require('express');
var sqlite = require('sqlite3');

var app = express();

var bodyParser = require("body-parser");
app.use(bodyParser.urlencoded({ extended: false }));
app.use(bodyParser.json());

var db = new sqlite.Database('logserver.db', (err) => {
    if (err) {
        console.error(err.message);
    }
});


// Take a date object and convert it into the format for the database,
// which is nearly the ISO format (but in the local timzeone)
function toSqlDate(date) {
    var z = date.getTimezoneOffset() * 60 * 1000;
    var tLocal = date - z ;
    var tLocal = new Date(tLocal);
    var iso = tLocal.toISOString();
    iso = iso.slice(0, 19);
    iso = iso.replace('T', ' ')

    return iso;    
}


// Generic function for getting a date range. Returns an array of
// start date/time and end date/time. By default, these will be the
// last 24 hours, but can be overridden by specifying either a day
// or a start-end day or time in request query. Returns parameters
// in ISO forrmat (which matches the database).
//
// NOTE: this does not canonicalize dates, so it doesn't add times to
// unqualified dates.
function getDates(req) {
    let now = new Date();
    let yesterday = new Date(now - 1000*60*60*24);

    // as far as I can tell, I can use "== undefined" to test if
    // something is undefined, but I cannot use "!= underfined" to
    // see if it is defined. That results in a rather messy
    // structure.
    if (req.query.day == undefined) {
	// DAY not defined, so use START/END or defaults
	if (req.query.start == undefined) {
	    start = toSqlDate(yesterday);   // default to most recent 24 hours
	} else {
	    start = req.query.start;
	}
	if (req.query.end == undefined) {
	    end = toSqlDate(now);           // default to most recent 24 hours
	} else {
	    end = req.query.end;
	}
    } else {
	// use DAY parameter
	start = req.query.day + " 00:00:00";
	end = req.query.day + " 23:59:59";
    }
    return [start, end];
}


// /STATUS end-point. Return a basic indicator that things are working
// (a count of the number of items logged in the last 24 hours).
app.get('/status', function(request, response){
    dates = getDates(request);
    var stmt = "SELECT COUNT(*) FROM log WHERE time > ? and time < ?"
    db.get(stmt, dates[0], dates[1], (err, row) => {
        if (err) {
	    response.status(400).send('Database error');
        } else {
            response.send(JSON.stringify(row));
        }
    });
});


// /PTEST end-point, for random testing.
app.get('/ptest', function(req, resp){
    dates = getDates(req);
    resp.send(JSON.stringify(dates));
});


// /DATA end-point. This is a basic query structure for the database.
// Query parameters are STREAM, START, END, DAY.
app.get("/data", (req, res, next) => {
    dates = getDates(req);
    stream = req.query.stream;
    var sql = 'select * from log where stream=?  and time > ? and time < ?';
    db.all(sql, stream, dates[0], dates[1], (err, rows) => {
        if (err) {
          res.status(400).json({"error":err.message});
          return;
        }
//        res.json({
//            "message":"success",
//            "data":rows
	//        })
	res.json(rows);
      });
});


// /MAX end-point. get max value in a given period, defaulting to the
// last 24 hours. query parameters are STREAM, START, END, DAY.
app.get('/max', (req, resp, next) => {
    let dates = getDates(req);
    
    var stmt = "SELECT time,MAX(data) FROM log WHERE stream = ? AND time > ? and time < ?"
	
    db.get(stmt, stream, dates[0], dates[1], (err, row) => {
        if (err) {
	    resp.status(400).send('Database error');
        } else {
            resp.send(JSON.stringify(row));
        }
    });
});


// /MIN end-point. get min value in a given period, defaulting to the
// last 24 hours. query parameters are STREAM, START, END, DAY.
app.get('/min', (req, resp, next) => {
    let dates = getDates(req);
    stream = req.query.stream;
    
    var stmt = "SELECT time,MIN(data) FROM log WHERE stream = ? AND time > ? and time < ?"
	
    db.get(stmt, stream, dates[0], dates[1], (err, row) => {
        if (err) {
	    resp.status(400).send('Database error');
        } else {
            resp.send(JSON.stringify(row));
        }
    });
});


// /AVG end-point. get average value in a given period, defaulting to the
// last 24 hours. query parameters are STREAM, START, END, DAY.
app.get('/avg', (req, resp, next) => {
    let dates = getDates(req);
    stream = req.query.stream;
    
    var stmt = "SELECT AVG(data) FROM log WHERE stream = ? AND time > ? and time < ?"
	
    db.get(stmt, stream, dates[0], dates[1], (err, row) => {
        if (err) {
	    resp.status(400).send('Database error');
        } else {
            resp.send(JSON.stringify(row));
        }
    });
});


// /LATEST end-porint. return the most recent data item and time.
// query parameters in STREAM.
app.get('/latest', (req, resp, next) => {
    stream = req.query.stream;

    var stmt = "SELECT time,data FROM log WHERE stream = ? ORDER BY time DESC LIMIT 1"
	
    db.get(stmt, stream, (err, row) => {
        if (err) {
	    resp.status(400).send('Database error');
        } else {
            resp.send(JSON.stringify(row));
        }
    });
});


// log data endpoints. The end-point here is the stream, so we need
// to catch anything and then extract the data from the query.
app.post('/:stream', function(req, resp){
    stream = req.params.stream;
    data = req.query.data;
    var stmt = db.prepare("INSERT INTO log VALUES (datetime('now','localtime'),?,?)");
    stmt.run(stream,data);
    resp.end();
});


// Default response for any other request
app.use(function(req, res){
    res.status(404);
});


// Start the server
app.listen(8080, function () {
    //console.log('Express server is listening on port 8080');
});
