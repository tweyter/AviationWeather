from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base


class Base(object):
    def __json__(self):
        json_response = {}
        if isinstance(self, AirSigmet):
            for x in getattr(self, 'points', []):
                x.__json__()
        elif isinstance(self, Metar):
            for x in getattr(self, 'sky_condition', []):
                x.__json__()
        elif isinstance(self, Taf):
            for x in getattr(self, 'forecast', []):
                x.__json__()
        elif isinstance(self, Forecast):
            sub_types = ('sky_condition', 'turbulence_condition', 'icing_condition')
            for sub_type in sub_types:
                json_response[sub_type] = [x.__json__() for x in getattr(self, sub_type, [])]

        json_exclude = getattr(self, '__json_exclude__', set())
        json_exclude.add("id")
        json_exclude.add("parent_id")
        json_response.update(
            {key: value for key, value in self.__dict__.items()
                # Do not serialize 'private' attributes
                # (SQLAlchemy-internal attributes are among those, too)
                if not key.startswith('_')
                and key not in json_exclude}
        )
        return json_response


Base = declarative_base(cls=Base)


class Points(Base):
    __tablename__ = "Points"

    id = Column(Integer, primary_key=True)
    parent_id = Column(Integer, ForeignKey('AirSigmet.id'))

    latitude = Column(Float)
    longitude = Column(Float)

    airsigmet = relationship("AirSigmet", back_populates="area")

    def __repr__(self):
        repr_string = "Points({latitude}, {longitude})".format(
            latitude=self.latitude, longitude=self.longitude
        )
        return repr_string


class AirSigmet(Base):
    __tablename__ = 'AirSigmet'

    id = Column(Integer, primary_key=True)

    raw_text = Column(String(2000))
    valid_time_from = Column(DateTime)
    valid_time_to = Column(DateTime)
    airsigmet_type = Column(String(30))
    hazard__type = Column(String(30))
    hazard__severity = Column(String(30))
    altitude__min_ft_msl = Column(Integer)
    altitude__max_ft_msl = Column(Integer)
    movement_dir_degrees = Column(Integer)
    movement_speed_kt = Column(Integer)
    area__num_points = Column(Integer)
    area = relationship("Points", order_by=Points.id, back_populates="airsigmet")

    def __repr__(self):
        return "AirSigmet({raw_text}, {valid_time_from}, {valid_time_to}, " \
               "{airsigmet_type}, {hazard__type}, {hazard__severity}, " \
               "{altitude__min_ft_msl}, {altitude__max_ft_msl}, " \
               "{area__num_points})".format(
                    raw_text=self.raw_text,
                    valid_time_from=self.valid_time_from,
                    valid_time_to=self.valid_time_to,
                    airsigmet_type=self.airsigmet_type,
                    hazard__type=self.hazard__type,
                    hazard__severity=self.hazard__severity,
                    altitude__min_ft_msl=self.altitude__min_ft_msl,
                    altitude__max_ft_msl=self.altitude__max_ft_msl,
                    movement_dir_degrees=self.movement_dir_degrees,
                    movement_speed_kt=self.movement_speed_kt,
                    area__num_points=self.area__num_points
                )


class Forecast(Base):
    __tablename__ = "Forecast"

    id = Column(Integer, primary_key=True)
    parent_id = Column(Integer, ForeignKey('Taf.id'))

    time_from = Column(DateTime)
    time_to = Column(DateTime)
    change_indicator = Column(String(30))
    time_becoming = Column(DateTime)
    probability = Column(Integer)
    wind_dir_degrees = Column(Integer)
    wind_speed_kt = Column(Integer)
    wind_gust_kt = Column(Integer)
    wind_shear_hgt_ft_agl = Column(Integer)
    wind_shear_dir_degrees = Column(Integer)
    wind_shear_speed_kt = Column(Integer)
    visibility_statute_mi = Column(Float)
    altim_in_hg = Column(Float)
    vert_vis_ft = Column(Integer)
    wx_string = Column(String(500))
    not_decoded = Column(String(500))
    taf = relationship("Taf", back_populates="forecast")
    sky_condition = relationship("SkyCondition", back_populates="forecast")
    turbulence_condition = relationship("TurbulenceCondition", back_populates="forecast")
    icing_condition = relationship("IcingCondition", back_populates="forecast")

    def __repr__(self):
        return "Forecast({time_from}, {time_to}, {change_indicator}, {time_becoming}, {probability}, " \
               "{wind_dir_degrees}, {wind_speed_kt}, {wind_gust_kt}, {wind_shear_hgt_ft_agl}, " \
               "{wind_shear_dir_degrees}, {wind_shear_speed_kt}, {visibility_statute_mi}, " \
               "{altim_in_hg}, {vert_vis_ft}, {wx_string}, {not_decoded})".format(
                time_from=self.time_from,
                time_to=self.time_to,
                change_indicator=self.change_indicator,
                time_becoming=self.time_becoming,
                probability=self.probability,
                wind_dir_degrees=self.wind_dir_degrees,
                wind_speed_kt=self.wind_speed_kt,
                wind_gust_kt=self.wind_gust_kt,
                wind_shear_hgt_ft_agl=self.wind_shear_hgt_ft_agl,
                wind_shear_dir_degrees=self.wind_shear_dir_degrees,
                wind_shear_speed_kt=self.wind_shear_speed_kt,
                visibility_statute_mi=self.visibility_statute_mi,
                altim_in_hg=self.altim_in_hg,
                vert_vis_ft=self.vert_vis_ft,
                wx_string=self.wx_string,
                not_decoded=self.not_decoded,
                )


class Taf(Base):
    __tablename__ = "Taf"
    
    id = Column(Integer, primary_key=True)

    raw_text = Column(String(2000))
    station_id = Column(String(30))
    issue_time = Column(DateTime)
    bulletin_time = Column(DateTime)
    valid_time_from = Column(DateTime)
    valid_time_to = Column(DateTime)
    remarks = Column(String(500))
    latitude = Column(Float)
    longitude = Column(Float)
    elevation_m = Column(Float)
    forecast = relationship("Forecast", order_by=Forecast.id, back_populates="taf")

    def __repr__(self):
        return "Taf({raw_text}, {station_id}, {issue_time}, {bulletin_time}, {valid_time_from}, " \
               "{valid_time_to}, {remarks}, {latitude}, {longitude}, {elevation_m})".format(
                raw_text=self.raw_text,
                station_id=self.station_id,
                issue_time=self.issue_time,
                bulletin_time=self.bulletin_time,
                valid_time_from=self.valid_time_from,
                valid_time_to=self.valid_time_to,
                remarks=self.remarks,
                latitude=self.latitude,
                longitude=self.longitude,
                elevation_m=self.elevation_m
                )


class SkyCondition(Base):
    __tablename__ = "SkyCondition"
    
    id = Column(Integer, primary_key=True)
    parent_id = Column(Integer, ForeignKey('Forecast.id'))

    sky_cover = Column(String(30))
    cloud_base_ft_agl = Column(Integer)
    cloud_type = Column(String(30))
    forecast = relationship("Forecast", back_populates="sky_condition")

    def __repr__(self):
        return "SkyCondition({sky_cover}, {cloud_base_ft_agl}, {cloud_type})".format(
                sky_cover=self.sky_cover,
                cloud_base_ft_agl=self.cloud_base_ft_agl,
                cloud_type=self.cloud_type,
                )


class TurbulenceCondition(Base):
    __tablename__ = "TurbulenceCondition"
    
    id = Column(Integer, primary_key=True)
    parent_id = Column(Integer, ForeignKey('Forecast.id'))

    turbulence_intensity = Column(String(30))
    turbulence_min_alt_ft_agl = Column(Integer)
    turbulence_max_alt_ft_agl = Column(Integer)
    forecast = relationship("Forecast", back_populates="turbulence_condition")

    def __repr__(self):
        return "TurbulenceCondition({turbulence_intensity}, {turbulence_min_alt_ft_agl}, " \
               "{turbulence_max_alt_ft_agl})".format(
                turbulence_intensity=self.turbulence_intensity,
                turbulence_min_alt_ft_agl=self.turbulence_min_alt_ft_agl,
                turbulence_max_alt_ft_agl=self.turbulence_max_alt_ft_agl,
                )


class IcingCondition(Base):
    __tablename__ = "IcingCondition"
    
    id = Column(Integer, primary_key=True)
    parent_id = Column(Integer, ForeignKey('Forecast.id'))

    icing_intensity = Column(String(30))
    icing_min_alt_ft_agl = Column(Integer)
    icing_max_alt_ft_agl = Column(Integer)
    forecast = relationship("Forecast", back_populates="icing_condition")

    def __repr__(self):
        return "IcingCondition({icing_intensity}, {icing_min_alt_ft_agl}, {icing_max_alt_ft_agl})".format(
            icing_intensity=self.icing_intensity,
            icing_min_alt_ft_agl=self.icing_min_alt_ft_agl,
            icing_max_alt_ft_agl=self.icing_max_alt_ft_agl,
        )


class Metar(Base):
    __tablename__ = "Metar"

    id = Column(Integer, primary_key=True)

    raw_text = Column(String(2000))
    station_id = Column(String(30))
    observation_time = Column(DateTime)
    latitude = Column(Float)
    longitude = Column(Float)
    temp_c = Column(Float)
    dewpoint_c = Column(Float)
    wind_dir_degrees = Column(Integer)
    wind_speed_kt = Column(Integer)
    wind_gust_kt = Column(Integer)
    visibility_statute_mi = Column(Float)
    altim_in_hg = Column(Float)
    sea_level_pressure_mb = Column(Float)
    quality_control_flags = Column(String(30))
    wx_string = Column(String(30))
    flight_category = Column(String(30))
    three_hr_pressure_tendency_mb = Column(Float)
    maxT_c = Column(Float)
    minT_c = Column(Float)
    maxT24hr_c = Column(Float)
    minT24hr_c = Column(Float)
    precip_in = Column(Float)
    pcp3hr_in = Column(Float)
    pcp6hr_in = Column(Float)
    pcp24hr_in = Column(Float)
    snow_in = Column(Float)
    vert_vis_ft = Column(Float)
    metar_type = Column(String(30))
    elevation_m = Column(Float)

    sky_condition = relationship("MetarSkyCondition", back_populates="metar")

    def __repr__(self):
        return "Metar(" \
                "{raw_text},"\
                "{station_id},"\
                "{observation_time},"\
                "{latitude},"\
                "{longitude},"\
                "{temp_c},"\
                "{dewpoint_c},"\
                "{wind_dir_degrees},"\
                "{wind_speed_kt},"\
                "{wind_gust_kt},"\
                "{visibility_statute_mi},"\
                "{altim_in_hg},"\
                "{sea_level_pressure_mb},"\
                "{quality_control_flags},"\
                "{wx_string},"\
                "{flight_category},"\
                "{three_hr_pressure_tendency_mb},"\
                "{maxT_c},"\
                "{minT_c},"\
                "{maxT24hr_c},"\
                "{minT24hr_c},"\
                "{precip_in},"\
                "{pcp3hr_in},"\
                "{pcp6hr_in},"\
                "{pcp24hr_in},"\
                "{snow_in},"\
                "{vert_vis_ft},"\
                "{metar_type},"\
                "{elevation_m},"\
                ")".format(
                    raw_text=self.raw_text,
                    station_id=self.station_id,
                    observation_time=self.observation_time,
                    latitude=self.latitude,
                    longitude=self.longitude,
                    temp_c=self.temp_c,
                    dewpoint_c=self.dewpoint_c,
                    wind_dir_degrees=self.wind_dir_degrees,
                    wind_speed_kt=self.wind_speed_kt,
                    wind_gust_kt=self.wind_gust_kt,
                    visibility_statute_mi=self.visibility_statute_mi,
                    altim_in_hg=self.altim_in_hg,
                    sea_level_pressure_mb=self.sea_level_pressure_mb,
                    quality_control_flags=self.quality_control_flags,
                    wx_string=self.wx_string,
                    flight_category=self.flight_category,
                    three_hr_pressure_tendency_mb=self.three_hr_pressure_tendency_mb,
                    maxT_c=self.maxT_c,
                    minT_c=self.minT_c,
                    maxT24hr_c=self.maxT24hr_c,
                    minT24hr_c=self.minT24hr_c,
                    precip_in=self.precip_in,
                    pcp3hr_in=self.pcp3hr_in,
                    pcp6hr_in=self.pcp6hr_in,
                    pcp24hr_in=self.pcp24hr_in,
                    snow_in=self.snow_in,
                    vert_vis_ft=self.vert_vis_ft,
                    metar_type=self.metar_type,
                    elevation_m=self.elevation_m,
                )


class MetarSkyCondition(Base):
    __tablename__ = "MetarSkyCondition"

    id = Column(Integer, primary_key=True)
    parent_id = Column(Integer, ForeignKey('Metar.id'))

    sky_cover = Column(String(30))
    cloud_base_ft_agl = Column(Integer)
    cloud_type = Column(String(30))
    metar = relationship("Metar", back_populates="sky_condition")

    def __repr__(self):
        return "SkyCondition({sky_cover}, {cloud_base_ft_agl}, {cloud_type})".format(
            sky_cover=self.sky_cover,
            cloud_base_ft_agl=self.cloud_base_ft_agl,
            cloud_type=self.cloud_type,
        )
