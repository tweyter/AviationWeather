===============
AviationWeather
===============


Requires a config.ini file in the source package directory (the same directory as the source code).
The config file should have the following elements:

['sqlalchemy']

drivername = mysql+pymysql

username = mysql username

password = mysql username's password

host = host address (localhost or IP address)

port = should be 3306

database = should be aviationweather

[logging]

environment = development or testing or production

logpath = path to log file (make sure permissions are correct)

[flightaware.com]

username = fcview

api_key = fcview's FlightAware V3 api key goes here.
