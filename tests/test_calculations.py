import datetime
from collections import OrderedDict
import json

from sqlalchemy.orm.session import Session
from pygeodesy.sphericalNvector import LatLon
from lxml import etree
from dateutil import parser

import calculations
from sql_classes import AirSigmet, Points, Metar, Taf


def test_test_equality():
    latlon1 = LatLon(0, 0)
    latlon2 = latlon1
    result = calculations.test_equality(latlon1, latlon2)
    assert result is True


def test_airport_latlon():
    kord = (41.97859955, -87.90480042)
    kord_latlon = LatLon(*kord)
    result = calculations.airport_latlon("KORD")
    assert kord_latlon == result


def test_get_db_session():
    """
    There is probably no need to test this.
    """
    assert True is True


def test_airsigmets(dbsession: Session):
    departure = 1514808000  # 2018-1-1T12:00:00
    arrival = departure
    field_values = {
        "raw_text": str(),
        "valid_time_from": datetime.datetime.utcfromtimestamp(departure),
        "valid_time_to": datetime.datetime.utcfromtimestamp(arrival),
        "airsigmet_type": str(),
        "hazard__type": str(),
        "hazard__severity": str(),
        "altitude__min_ft_msl": int(),
        "altitude__max_ft_msl": int(),
        # "movement_dir_degrees": int(),
        # "movement_speed_kt": int(),
        "area__num_points": int(),
    }
    airsig = AirSigmet(**field_values)
    dbsession.add(airsig)
    result = calculations.airsigmets(dbsession, arrival, departure)
    assert [airsig] == result


def test_airsigmet_points():
    airsig = AirSigmet()
    p1 = OrderedDict(latitude=0, longitude=0)
    p2 = OrderedDict(latitude=1, longitude=1)
    airsig.area = [Points(**p1), Points(**p2)]
    perimeter = [(LatLon(*p1.values()), LatLon(*p2.values())), (LatLon(*p2.values()), LatLon(*p1.values()))]
    result = calculations.airsigmet_points(airsig)
    assert perimeter == result


def test_find_intersection():
    start1 = LatLon(0, 0)
    end1 = LatLon(0, 2)
    airsig = AirSigmet()
    airsig.area = [Points(latitude=1, longitude=1), Points(latitude=-1, longitude=1)]
    result = calculations.find_intersection(start1, end1, airsig)
    assert [LatLon(0, 1), LatLon(0, 1)] == result


def test_find_intersecting_airsigs(monkeypatch):
    def mockreturn(s1, s2, airsig):
        return airsig
    monkeypatch.setattr(calculations, 'find_intersection', mockreturn)
    airsigs = [AirSigmet()]
    route = [(LatLon(0, 0), LatLon(1, 1))]
    result = calculations.find_intersecting_airsigs(airsigs, route)
    assert airsigs == result


def test_get_flightaware_client():
    """
    Probably don't need to test this.
    """
    assert True is True


class Service:

    def __init__(self, faflightid, departure_time, dep_apt='', arr_apt=''):
        self.faflightid = faflightid
        self.departure_time = departure_time
        self.departure_airport = dep_apt
        self.arrival_airport = arr_apt

    def FlightInfoStatus(self, *args):
        assert 'JBU669' == args[0]
        departure = {"epoch": self.departure_time}
        arrival = {"epoch": 0}
        flight = {
            "faFlightID": self.faflightid,
            "filed_departure_time": departure,
            "estimated_arrival_time": arrival,
            "origin": {"code": self.departure_airport},
            "destination": {"code": self.arrival_airport},
        }
        return {"flights": [flight]}

    def DecodeFlightRoute(self, *args):
        assert self.faflightid == args[0]
        return {'data': [
            {'latitude': 0, 'longitude': 0},
            {'latitude': 1, 'longitude': 1}
        ]}


class MockClient:
    def __init__(self, faflightid, departure_time, dep_apt='', arr_apt=''):
        self.service = Service(faflightid, departure_time, dep_apt, arr_apt)


def test_get_flightinfostatus():
    faflightid = 'abc123'
    flt_num = 'JBU669'
    dep = 'KSAN'
    arr = 'KBOS'
    departure_time = 0
    client = MockClient(faflightid, departure_time, dep, arr)
    result = calculations.get_flightinfostatus(flt_num, departure_time, client)
    assert (faflightid, departure_time, dep, arr) == result


def test_get_flight_route_data():
    faflightid = 'abc123'
    departure_time = 0
    client = MockClient(faflightid, departure_time)
    segments = [
        (LatLon(0, 0), LatLon(1, 1)),
    ]
    result = calculations.get_flight_route_data(client, faflightid)
    assert segments == result


def test_get_metar_data(dbsession: Session):
    metar = Metar(station_id='KJFK')
    dbsession.add(metar)
    dbsession.commit()
    result = calculations.metars(dbsession, 'KJFK', 'KJFK')
    assert [metar] == result[0]


def test_output():
    data = etree.parse('/home/thorsten/PycharmProjects/XMLtoSQL/tests/test_data/airsigmet.xml')
    m = data.find('data')
    m_data = m.find('AIRSIGMET')
    airsig = AirSigmet(
        airsigmet_type=m_data.find('airsigmet_type').text,
        valid_time_from=parser.parse(m_data.find('valid_time_from').text)
    )
    check = [{"valid_time_from": 1539506700.0, "airsigmet_type": "AIRMET"}]
    result = calculations.output([airsig])
    assert check == json.loads(result)


def test_metar_output():
    data = etree.parse('/home/thorsten/PycharmProjects/XMLtoSQL/tests/test_data/metar.xml')
    m = data.find('data')
    m_data = m.find('METAR')
    metar = Metar(
        station_id=m_data.find('station_id').text,
        observation_time=parser.parse(m_data.find('observation_time').text)
    )
    check = {
        'departure': {"observation_time": 1541900400.0, 'sky_condition': [], "station_id": "KSTK"},
        'arrival': {"observation_time": 1541900400.0, 'sky_condition': [], "station_id": "KSTK"}
    }
    result = calculations.metar_output(metar, metar)
    assert check == json.loads(result)


def test_tafs(dbsession: Session):
    departure_airport = 'KJFK'
    departure_time = 1541900400.0
    arrival_airport = 'KSAN'
    arrival_time = 1541900500.0
    dep_taf = Taf(
        station_id=departure_airport,
        valid_time_from=datetime.datetime.utcfromtimestamp(departure_time),
        valid_time_to=datetime.datetime.utcfromtimestamp(departure_time),
    )
    arr_taf = Taf(
        station_id=arrival_airport,
        valid_time_from=datetime.datetime.utcfromtimestamp(arrival_time),
        valid_time_to=datetime.datetime.utcfromtimestamp(arrival_time),
    )
    dbsession.add_all([dep_taf, arr_taf])
    dbsession.commit()
    result = calculations.tafs(
        dbsession,
        departure_airport, departure_time, arrival_airport, arrival_time
    )
    assert [dep_taf, arr_taf] == result


def test_tafs2(db_sample: Session):
    epoch = 1542697200.0  # 2018-11-20 02:00:00
    departure_airport = 'KRDR'
    arrival_airport = 'KIND'
    result = calculations.tafs(db_sample, departure_airport, epoch, arrival_airport, epoch)
    assert result[0].station_id == 'KRDR'
