===============
AviationWeather
===============


Requires a config.ini file in the top directory (the same directory as this README file).
The config file should have the following elements:

['sqlalchemy']

drivername = mysql+pymysql

username = mysql username

password = mysql username's password

host = host address (localhost or IP address)

port = should be 3306

[logging]

environment = development or testing or production

logpath = path to log file (make sure permissions are correct)
