CONFIGURATION GUIDE
===================

The AviationWeather program requires a configuration file called "config.ini" to be
in the project's root folder (ie. the same location as /src /docs etc.)

config.ini requires the three following sub-headings: sqlalchemy, flightaware.com and logging
The configuration settings for each sub-heading are as follows:

*sqlalchemy*
  * drivername: Should be mysql+pymysql unless we switch to a different database such as postgresql
  * username: The username for database access.
  * password: The database access password for the given username.
  * host: Host address of the database. Either localhost or a URL.
  * port: Port number for the database. If local, it should be 3306.
  * database: The name of the database schema to be used.

*flightaware.com*
  * username: The username for FlightAware API access.
  * api_key: The API key for FlightAware API access.

*logging*
  * environment: The environment of the current program, whether a development machine (our laptops), the testing server, or a production server. Choices are:
    1. development
    2. testing
    3. production

  * logpath: The file path where you would like error logs to be located. If the path does not yet exist it will be automatically created.

Example
--------

::

  [sqlalchemy]
  drivername = mysql+pymysql
  username = root
  password = mysupersecretpassword
  host = localhost
  port = 3306
  database = sample_data
  [flightaware.com]
  username = fcview
  api_key = 123ABC789XYZ
  [logging]
  environment = development
  logpath = /home/someuser/code/aviationweather/logs
