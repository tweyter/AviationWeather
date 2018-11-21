import os.path
import gzip

from sqlalchemy.orm.session import Session
from lxml import etree

import converter
from src.sql_classes import AirSigmet, Metar, MetarSkyCondition
from src.xml_classes import SkyConditionXML, TurbulenceConditionXML


def test_get_data():
    """
    There is probably no need to test this.
    """
    assert True is True


def test_bytes_to_xml():
    root = etree.Element("root")
    data = gzip.compress(etree.tostring(root))
    result = converter.bytes_to_xml(data)
    assert etree.tostring(root) == etree.tostring(result)


def test_bytes_to_xml_metar_data():
    pth = os.path.join(os.path.dirname(__file__), 'test_data', 'metars.cache.xml.gz')

    with open(pth, 'rb') as f:
        data = f.read()
    result = converter.bytes_to_xml(data)
    assert 'response' == result.tag


def test_convert_airsigmets():
    pth = os.path.join(os.path.dirname(__file__), 'test_data', 'airsigmet.xml')
    root = etree.parse(pth)
    maps = converter.convert_airsigmets(root)
    assert maps[0].altitude__min_ft_msl == 17000


def test_get_db_session():
    """
    There is probably no need to test this.
    """
    assert True is True


def test_to_db(dbsession: Session):
    airsig = AirSigmet()
    converter.to_db([airsig], dbsession)
    assert [airsig] == dbsession.query(AirSigmet).all()


def test_process_sky_condition():
    data = etree.XML('<sky_condition sky_cover="FEW" cloud_base_ft_agl="4000" />')
    result = converter.process_attrib(data)
    check = SkyConditionXML(sky_cover="FEW", cloud_base_ft_agl=4000)
    assert check.attributes() == result.attributes()


def test_process_turbulence_condition():
    data = etree.XML('<turbulence_condition turbulence_intensity="MOD" turbulence_min_alt_ft_agl="4000" />')
    result = converter.process_attrib(data)
    check = TurbulenceConditionXML(turbulence_intensity="MOD", turbulence_min_alt_ft_agl=4000)
    assert check.attributes() == result.attributes()


def test_convert_tafs():
    pth = os.path.join(os.path.dirname(__file__), 'test_data', 'jfk_taf_sample.xml')
    root = etree.parse(pth)
    maps = converter.convert_tafs(root)
    assert "KJFK" == maps[0].station_id


def test_convert_metars():
    pth = os.path.join(os.path.dirname(__file__), 'test_data', 'metar.xml')
    root = etree.parse(pth)
    maps = converter.convert_metars(root)
    assert "KSTK" == maps[0].station_id


def test_metars_to_db(dbsession: Session):
    pth = os.path.join(os.path.dirname(__file__), 'test_data', 'metar.xml')
    root = etree.parse(pth)
    maps = converter.convert_metars(root)
    converter.to_db(maps, session=dbsession)
    assert maps == dbsession.query(Metar).all()
    sky_condition = maps[0].sky_condition[0]
    assert isinstance(sky_condition, MetarSkyCondition)
    result = dbsession.query(MetarSkyCondition).all()
    assert [sky_condition] == result
