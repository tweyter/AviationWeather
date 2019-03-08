===============
AviationWeather
===============

------------
Installation
------------

This program uses the lxml library for parsing XML. Installing it on Ubuntu requires
binaries to be installed. To do so, type the following on the command line::

    sudo apt-get install libxml2-dev libxslt1-dev python-dev

After that, create a Python virtual environment. Pyenv and pyenv-virtualenv should already
be installed on the FCV servers for the user tweyter. The files are located under /home/tweyter/.pyenv  If a separate installation of pyenv is required, then there are a few
additional steps to take::

    sudo apt-get install build-essential git libreadline-dev zlib1g-dev libssl-dev libbz2-dev libsqlite3-dev

Then follow the directions in https://github.com/pyenv/pyenv-installer

Once installed, use 'pyenv install' to install a Python interpreter::

    pyenv install 3.6.6

You will also need pyenv-virtualenv. To install::

    git clone https://github.com/pyenv/pyenv-virtualenv.git $PYENV_ROOT/plugins/pyenv-virtualenv

Then to create a virtualenv, type the following, where <name of venv>
is the name you choose to call the virtualenv (I recommend naming it avwx_venv for consistency).::

    pyenv virtualenv 3.6.1 <name of venv>

Then activate the virtualenv by typing::

    pyenv activate <name of venv>

This will switch to using the virtualenv's Python interpreter.

Then go to the directory where you want the package to be installed, and clone it via git. This requires
github access from the server, whether via username/password or via ssh-public-key copied from the server to github::

    git clone git@github.com:tweyter/AviationWeather.git

Once installed, cd into the AviationWeather directory, and type::

    python setup.py install

-------------
Configuration
-------------

Requires a config.ini file in the source package directory (the same directory as the source code).
The config file should have the following elements:

::

    [sqlalchemy]
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

----------------------
Command line operation
----------------------

The Python interpreter for this program is located at:

/home/tweyter/.pyenv/versions/avwx_venv/bin/python

To run the converter program, use the following command:

converter <weather type>

Where weather type is one of "metar", "taf" or "airsigmet"

Example::

/home/tweyter/.pyenv/versions/avwx_venv/bin/python converter metar


If you installed a separate version of pyenv, then use your $PYENV_ROOT::

$PYENV_ROOT/versions/bin/<name of venv>/bin converter metar

To use the calculations program, the command is similar,
The command is 'calculations' followed by the weather type request (metar,
taf, or airsigmet) followed by the flight-id (3-letter airline + flight number),
then departure airport, then arrival airport, then optional departure time in
epoch format.  Example: ::

$PYENV_ROOT/versions/bin/<name of venv>/bin calculations metar DAL124 JFK LAX

The output is then sent to stdout