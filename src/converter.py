"""
Downloads either Airmet/Sigmet, Taf, or Metar data from www.aviationweather.gov
then stores the data in an SQL database for future retrieval.

"""
import configparser
import os.path
from typing import List, Union
import gzip
import sys
import logging

from lxml import etree
from lxml.etree import Element
from sqlalchemy import create_engine
from sqlalchemy.engine.url import URL
from sqlalchemy.orm import sessionmaker, Session
import requests

from src.sql_classes import AirSigmet, Taf, Metar
from src.xml_classes import AirSigmetXML2, PointsXML2, TafXML, ForecastXML, SkyConditionXML
from src.xml_classes import TurbulenceConditionXML, IcingConditionXML
from src.xml_classes import MetarXML, MetarSkyConditionXML
import logging_setup


logging_setup.setup()
logger = logging.getLogger(__name__)


def get_data(weather_type: str) -> bytes:
    """
    Get the raw XML data for the weather type requested.

    :param weather_type:     Weather type can be airsigmet, taf, or metar.
    :return: etree data
    """
    base_url = "https://www.aviationweather.gov/adds/dataserver_current/current/"
    if weather_type == 'airsigmet':
        url = base_url + "airsigmets.cache.xml.gz"
    elif weather_type == 'taf':
        url = base_url + "tafs.cache.xml.gz"
    elif weather_type == 'metar':
        url = base_url + "metars.cache.xml.gz"
    else:
        raise ValueError('Requested weather type must be either "airsigmet", "taf", or "metar".')
    req = requests.get(url)
    return req.content


def bytes_to_xml(xml_bytes: bytes) -> bytes:
    """
    Decompress GZIP data.

    :param xml_bytes: Raw gzipped bytes.
    :return: Unzipped data (in bytes)
    """
    data = gzip.decompress(xml_bytes)
    try:
        xml_data = etree.XML(data)
    except etree.XMLSyntaxError:
        data = gzip.decompress(data)
    else:
        return xml_data

    # Data was double-compressed
    xml_data = etree.XML(data)
    return xml_data


def convert_airsigmets(root: etree) -> List[AirSigmet]:
    """
    Iterate through the airsigmets and their child data.

    :param root: Etree root.
    :return: Mapped data.
    """

    def process(
            kids: List[Element],
            asigx: Union[AirSigmetXML2, PointsXML2]
    ) -> Union[AirSigmetXML2, PointsXML2]:
        """
        Process the XML data so that it can be mapped to the database.

        :param kids: child branches of the etree.
        :param asigx: AirSigmetXML2 class
        :return: AirSigmetXML2 with data.
        """
        for elt in kids:
            grandkids = list(elt)
            if elt.attrib:
                for k, v in elt.attrib.items():
                    kwarg = {"{}__{}".format(elt.tag, k): v}
                    asigx.set(**kwarg)
            else:
                kwarg = {elt.tag: elt.text}
                asigx.set(**kwarg)
            if grandkids:
                for grandchild in grandkids:
                    if grandchild.tag == "point":
                        asigx.add_child(process(grandchild.getchildren(), PointsXML2()))
                continue
        return asigx
    data = root.find("data")
    elems = data.findall("AIRSIGMET")
    maps = []
    for elm in elems:
        children = list(elm)
        proc = process(children, AirSigmetXML2())
        mapped = proc.create_mapping()
        maps.append(mapped)
    return maps


def process_attrib(attrib: etree) -> Union[SkyConditionXML, TurbulenceConditionXML, IcingConditionXML]:
    """
    Parse XML attributes of Taf data.

    :param attrib: The XML attribute to be parsed.
    :return: Class containing relevant attribute data.
    """
    att_class = {
        'sky_condition': SkyConditionXML,
        'turbulence_condition': TurbulenceConditionXML,
        'icing_condition': IcingConditionXML,
    }
    if attrib.tag not in att_class.keys():
        raise ValueError()
    return att_class[attrib.tag](**{k: v for k, v in attrib.items()})


def process_attrib_metar(attrib: etree) -> MetarSkyConditionXML:
    """
    Parse XML attributes of Metar data.

    :param attrib: The attribute to be parsed.
    :return: Class containing the relevant attribute data.
    """
    att_class = {
        'sky_condition': MetarSkyConditionXML,
    }
    if attrib.tag not in att_class.keys():
        raise ValueError()
    return att_class[attrib.tag](**{k: v for k, v in attrib.items()})


def convert_tafs(root: etree) -> List[Taf]:
    """
    Convert Taf data for the database.

    :param root: XML etree root.
    :return: Lit of SQLAlchemy Base Taf classes.
    """

    def process(
            kids: List[Element],
            xml_class: Union[TafXML, ForecastXML]
    ) -> Union[TafXML, ForecastXML]:
        """
        Process the XML data so that it can be mapped to the database.

        :param kids: child branches of the etree.
        :param xml_class: Empty XML class object.
        :return: Instantiated class with loaded data.
        """
        for elt in kids:
            if elt.tag == "forecast":
                xml_class.add_child(process(list(elt), ForecastXML()))
                continue
            if elt.attrib:
                xml_class.add_child(process_attrib(elt))
            else:
                kwarg = {elt.tag: elt.text}
                xml_class.set(**kwarg)
        return xml_class
    data = root.find("data")
    elems = data.findall("TAF")
    maps = []
    for elm in elems:
        children = list(elm)
        proc = process(children, TafXML())
        mapped = proc.create_mapping()
        maps.append(mapped)
    return maps


def convert_metars(root: etree) -> List[Metar]:
    """
    Convert metar data for the database.

    :param root: XML etree root.
    :return: List of SQLAlchemy Base classes for Metars.
    """
    def process(
            kids: List[Element],
            xml_class: MetarXML
    ) -> MetarXML:
        """
        Process the XML data so that it can be mapped to the database.

        :param kids: child branches of the etree.
        :param xml_class: Empty XML class object.
        :return: Instantiated class with loaded data.
        """
        for elt in kids:
            if elt.attrib:
                xml_class.add_child(process_attrib_metar(elt))
            else:
                kwarg = {elt.tag: elt.text}
                xml_class.set(**kwarg)
        return xml_class
    data = root.find("data")
    elems = data.findall("METAR")
    maps = []
    for elm in elems:
        children = list(elm)
        proc = process(children, MetarXML())
        mapped = proc.create_mapping()
        maps.append(mapped)
    return maps


def get_db_session(config: configparser.ConfigParser) -> Session:
    """
    Open a database session.

    :param config: Database username, password, etc.
    :return: Returns a live database session.
    """
    url = URL(
        config['sqlalchemy']['drivername'],
        config['sqlalchemy']['username'],
        config['sqlalchemy']['password'],
        config['sqlalchemy']['host'],
        config['sqlalchemy']['port'],
        config['sqlalchemy']['database'],
    )
    engine = create_engine(url)
    session_maker = sessionmaker(bind=engine)
    session = session_maker()
    return session


def to_db(maps: List[Union[AirSigmet, Taf, Metar]], session: Session):
    """
    Commit the data to the database.

    :param maps: The mapped data.
    :param session: The current database session.
    """

    # Create the table if necessary.
    engine = session.bind.engine
    base_object = maps[0]
    base_object.metadata.create_all(engine)

    # Add mappings and commit to the database.
    session.add_all(maps)
    session.commit()


def main(args):
    """
    Download raw XML data, process it, then store the processed data into the database.

    """
    wx_types = {'airsigmet', 'taf', 'metar'}
    if len(args) < 2:
        msg = "A weather type must be given: {}".format(wx_types)
        print(msg)
        return
    if args[1] not in wx_types:
        msg = "Incorrect weather type given: {}".format(args[1])
        logger.error(msg)
        raise ValueError('You must include an argument stating which weather type {} you wish to store.'.format(wx_types))
    weather_type = args[1]
    config = configparser.ConfigParser()
    config.read(
        os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "config.ini",
        )
    )
    xml_bytes = get_data(weather_type)
    raw_xml = bytes_to_xml(xml_bytes)
    if weather_type == 'airsigmet':
        mapd = convert_airsigmets(raw_xml)
    elif weather_type == 'taf':
        mapd = convert_tafs(raw_xml)
    elif weather_type == 'metar':
        mapd = convert_metars(raw_xml)
    else:
        return
    db_session = get_db_session(config)
    to_db(mapd, db_session)


if __name__ == "__main__":
    main(sys.argv)
