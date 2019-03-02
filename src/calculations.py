"""
Start with basic flight information. Airline, flight number, and departure date and time.
Get flight route information, including the faFlightID, departure time, and estimated arrival time.
Get all AirSigmets that fall within the time window between scheduled departure time and
estimated arrival time.
Cross reference route segments with AirSigmet area to see if they cross.
If so, return the full AirSigmet data.
"""
import csv
import configparser
import json
import sys
import os.path
from datetime import datetime
import logging
from typing import List, Tuple

from pygeodesy.sphericalNvector import intersection, LatLon
from pygeodesy.dms import parseDMS
from sqlalchemy import create_engine
from sqlalchemy.engine.url import URL
from sqlalchemy.orm import sessionmaker, subqueryload, Session
from sqlalchemy.exc import ArgumentError, OperationalError
from requests import Session as RequestSession
from requests.auth import HTTPBasicAuth
from zeep import Client
from zeep.transports import Transport

from src.sql_classes import Base, AirSigmet, Taf, Metar
from src import logging_setup


logging_setup.setup()
logger = logging.getLogger(__name__)
AIRPORT_DATA = {}

# Load airport information
with open(
        os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "static",
            "airports.csv",
        )
) as file:
    csvdata = csv.reader(file, delimiter=',', quotechar='"')
    for line in csvdata:
        AIRPORT_DATA[line[5]] = tuple(line)


def test_equality(latlon1: LatLon, latlon2: LatLon) -> bool:
    """
    Compare two LatLon object to see if they represent the same point.

    :param latlon1: First LatLon object to be compared.
    :param latlon2: Second LatLon object to be compared.
    :return: True if the points are the same.
    """
    if latlon1.lat == latlon2.lat and latlon1.lon == latlon2.lon:
        return True
    return False


def airport_latlon(airport: str) -> LatLon:
    """
    Find the latitude and longitude of an airport given that airport's 4-letter ICAO identifier.

    :param airport:  Airport's 4-letter ICAO identifier.
    :return: LatLon object containing the airports latitude and longitude.
    """
    db_listing = AIRPORT_DATA.get(airport)
    lat = db_listing[6]
    long = db_listing[7]
    return LatLon(parseDMS(lat, sep=':'), parseDMS(long, sep=':'))


def get_db_session(config: configparser.ConfigParser) -> Session:
    """
    Open a database session.

    :return: Returns the database session.
    """
    # url = URL('mysql+pymysql', 'root', 'scuzzlebutt', 'localhost', '3306', 'weatherV2')
    url = URL(
        config['sqlalchemy']['drivername'],
        config['sqlalchemy']['username'],
        config['sqlalchemy']['password'],
        config['sqlalchemy']['host'],
        config['sqlalchemy']['port'],
        config['sqlalchemy']['database'],
    )
    try:
        engine = create_engine(url)
    except ArgumentError:
        logger.exception('Badly formed URL. Please check your config file.')
        raise
    session_maker = sessionmaker(bind=engine)
    session = session_maker()
    try:
        session.query('1').from_statement('SELECT 1').all()
    except OperationalError:
        logger.exception("Could not connect to database. Check your config file and database connection.")
        raise
    return session


def tafs(
        session: Session,
        dep_apt: str,
        dep_time: float,
        arr_apt: str,
        arr_time: float,
):
    """
    Query Taf data from the database.

    :param session: The current database session.
    :param dep_apt: Departure airport.
    :param dep_time: Departure time.
    :param arr_apt: Arrival airport.
    :param arr_time: Arrival time.
    :return: Both departure and arrival Taf SQL objects.
    """
    dt = datetime.utcfromtimestamp(dep_time)
    at = datetime.utcfromtimestamp(arr_time)
    departure_taf = session.query(Taf).\
        filter(Taf.station_id == dep_apt).\
        filter(Taf.valid_time_from <= dt).\
        filter(Taf.valid_time_to >= dt).all()
    arrival_taf = session.query(Taf). \
        filter(Taf.station_id == arr_apt). \
        filter(Taf.valid_time_from <= at). \
        filter(Taf.valid_time_to >= at).all()

    return [departure_taf[0], arrival_taf[0]]


def metars(
        session: Session, dep_apt: str, arr_apt: str
) -> Tuple[List[Metar], List[Metar]]:
    """
    Query Metar data from the database.

    :param session: The current database session.
    :param dep_apt: Departure airport
    :param arr_apt: Arrival airport
    :return: Both departure and arrival Metar SQL objects.
    """
    departure_metars = session.query(Metar).\
        filter(Metar.station_id == dep_apt).\
        options(subqueryload(Metar.sky_condition)).all()
    arrival_metars = session.query(Metar). \
        filter(Metar.station_id == arr_apt). \
        options(subqueryload(Metar.sky_condition)).all()
    return departure_metars, arrival_metars


def airsigmets(session: Session, arrival: int, departure: int) -> List[AirSigmet]:
    """
    Query AirSigmet data from the database.

    :param session: The current database session.
    :param arrival: The arrival time of the flight being checked.
    :param departure: The departure time of the flight being checked.
    :return: All AirSigmets that meet the search criteria.
    """
    airsigs = session.query(AirSigmet).\
        filter(AirSigmet.valid_time_from >= datetime.utcfromtimestamp(departure)).\
        filter(AirSigmet.valid_time_to <= datetime.utcfromtimestamp(arrival)).\
        options(subqueryload(AirSigmet.area)).all()
    return airsigs


def airsigmet_points(airsig: AirSigmet) -> List[Tuple[LatLon, LatLon]]:
    """
    Create a list of tuples containing all the latitude and longitude points defining an airmet/
    sigmet area.

    :param airsig: The Airmet/Sigmet in question.
    :return: List of tuples defining the area.
    """
    points = [
        (
            LatLon(x.latitude, x.longitude),
            LatLon(y.latitude, y.longitude)
        ) for x, y in zip(airsig.area, airsig.area[1:])
    ]
    points.append((
        LatLon(airsig.area[-1].latitude, airsig.area[-1].longitude),
        LatLon(airsig.area[0].latitude, airsig.area[0].longitude),
    ))
    return points


def find_intersection(start1: LatLon, end1: LatLon, airsig: AirSigmet) -> List[LatLon]:
    """
    Find if a flight route segment intersects an airsigmet border.

    :param start1: Start of the route segment
    :param end1: End of the route segment.
    :param airsig: AirSigmet containing area lat-lon data.
    :return:
    """
    if test_equality(start1, end1):
        return []
    intersect_points = []
    for area_start, area_end in airsigmet_points(airsig):
        if test_equality(area_start, area_end):
            continue
        intersect_points.append(intersection(start1, end1, area_start, area_end))
    if any(intersect_points):
        return intersect_points
    return []


def find_intersecting_airsigs(airsigs: List[AirSigmet], route: List[Tuple[LatLon, LatLon]]) -> List[AirSigmet]:
    """
    Determine which airsigmets are intersected by the flight route.

    :param airsigs:
    :param route:
    :return:
    """
    intersects = []
    for airsig in airsigs:
        for segment in route:
            result = find_intersection(segment[0], segment[1], airsig)
            if result:
                intersects.append(airsig)
                break
    return intersects


def get_flightaware_client(config: configparser):
    """
    Set up the SOAP client for FlightAware.com

    :param config:
    :return:
    """
    username = config["flightaware.com"]["username"]
    apiKey = config["flightaware.com"]["api_key"]
    wsdlFile = 'https://flightxml.flightaware.com/soap/FlightXML3/wsdl'

    session = RequestSession()
    session.auth = HTTPBasicAuth(username, apiKey)
    client = Client(wsdlFile, transport=Transport(session=session))
    return client


def get_flightinfostatus(
        flt_num: str,
        departure_time: int,
        client
) -> tuple:
    """
    Get information for the flight in question.

    :param flt_num:
    :param departure_time:
    :param client:
    :return:
    """
    # todo: Change this to return departure and arrival airports as well.
    flight_info = client.service.FlightInfoStatus(flt_num)

    for flight in flight_info["flights"]:
        if flight["filed_departure_time"]["epoch"] == departure_time:
            return flight["faFlightID"], flight["estimated_arrival_time"]["epoch"], flight['origin']['code'], flight['destination']['code']
    return ()


def get_flight_route_data(client, flight_id):
    """
    Get the waypoint fixes and their latitudes and longitudes for the flight route.

    :param client:
    :param flight_id:
    :return:
    """
    route = client.service.DecodeFlightRoute(flight_id)

    points = []
    for waypoint in route['data']:
        points.append(
            LatLon(waypoint["latitude"], waypoint["longitude"])
        )
    segments = list(zip(points, points[1:]))
    return segments


def load_route():
    with open("DecodeFlightRoute.json") as f:
        route = json.load(f)
    points = [
        LatLon(waypoint.get("latitude"), waypoint.get("longitude")) for
        waypoint in route.get('data', [])
    ]
    segments = list(zip(points, points[1:]))
    return segments


def find_flight(departure_time: int):
    """
    Look up the flight in FlightAware and get the relevant information.

    :param departure_time: Epoch departure time.
    :return:
    """
    with open("FlightInfoStatus.json") as f:
        flight_info = json.load(f)
    for flight in flight_info.get("flights"):
        if flight["filed_departure_time"]["epoch"] == departure_time:
            return flight["faFlightID"], flight["estimated_arrival_time"]["epoch"]


class Encoder(json.JSONEncoder):
    """
    Convert objects such as date_times to JSON compatible formats.
    """
    def default(self, obj):
        if isinstance(obj, Base):
            return obj.__json__()
        elif isinstance(obj, datetime):
            return obj.timestamp()
        return json.JSONEncoder.default(self, obj)


def output(wx_data: List):
    out_data = []
    for item in wx_data:
        out_data.append(json.dumps(item, cls=Encoder))
    raw_json = json.dumps(wx_data, cls=Encoder)
    return raw_json


def metar_output(departure_metar, arrival_metar):
    formatted = {
        'departure': departure_metar,
        'arrival': arrival_metar,
    }
    raw_json = json.dumps(formatted, cls=Encoder)
    return raw_json


def main():
    wx_type, flt_num, departure_epoch = clean_args(sys.argv)
    config = configparser.ConfigParser()
    config.read(
        os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "config.ini",
        )
    )

    session = get_db_session(config)
    client = get_flightaware_client(config)
    flight_id, arrival_epoch, dep, arr = get_flightinfostatus(flt_num, departure_epoch, client)
    route = get_flight_route_data(client, flight_id)
    if wx_type == 'airsigmet':
        airsigs = airsigmets(session, departure_epoch, arrival_epoch)
        intersecting_airsigs = find_intersecting_airsigs(airsigs, route)
        result = output(intersecting_airsigs)
    elif wx_type == 'metar':
        metar_data = metars(session, dep, arr)
        result = metar_output(*metar_data)
    elif wx_type == 'taf':
        taf_data = tafs(session, dep, departure_epoch, arr, arrival_epoch)
        result = output(taf_data)
    else:
        raise ValueError("Must be one of airsigmet, metar, or taf.")
    print(result)


def clean_args(args):
    """
    Check for the correct number of arguments and make sure they are of the proper format.
    :param args: Command line arguments.
    :return: The cleaned arguments (weather type, flight number, and epoch departure time).
    """
    choices = {'airsigmet', 'taf', 'metar'}
    if len(args) != 4:
        return
    try:
        epoch_time = int(args[2])
    except TypeError:
        return
    if args[1] not in choices:
        return
    return args[1], args[2], epoch_time


if __name__ == "__main__":
    # faFlightID = 'JBU696-1540880773-airline-0132'
    # flight_num = "JBU696"
    # epoch = 1541107680
    main()
