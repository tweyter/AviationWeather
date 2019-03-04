import os.path
import gzip
import datetime

from sqlalchemy.orm.session import Session
from lxml import etree

from src.AviationWeather import converter
from src.AviationWeather.sql_classes import AirSigmet, Metar, MetarSkyCondition
from src.AviationWeather.xml_classes import SkyConditionXML, TurbulenceConditionXML


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


def test_delete_old_data(dbsession: Session):
    """
    Test to see that data older than 7 days is deleted, while data newer than 7 days is maintained.

    :param dbsession: test database
    """
    current_time = datetime.datetime.now()
    expiration_time = current_time - datetime.timedelta(days=10)
    raw_metar_data = dict(
        raw_text='sample',
        station_id='KPBI',
        observation_time=expiration_time,
    )
    old_metar = Metar(**raw_metar_data)
    raw_metar_data.update({'observation_time': current_time})
    new_metar = Metar(**raw_metar_data)
    dbsession.add_all((old_metar, new_metar,))
    dbsession.commit()
    converter.delete_old_data('metar', dbsession)
    check_old = dbsession.query(Metar).get(old_metar.id)
    assert check_old is None
    check_new = dbsession.query(Metar).get(new_metar.id)
    assert check_new is not None
