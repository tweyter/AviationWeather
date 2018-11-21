import datetime

from dateutil import parser

from src.sql_classes import AirSigmet, Points, Taf, Forecast
from src.sql_classes import SkyCondition, TurbulenceCondition, IcingCondition
from src.sql_classes import Metar, MetarSkyCondition


class XMLBaseClass:
    field_values = {}
    assigned = {}
    children = []

    def __init__(self, **kwargs):
        self.assigned = {x: False for x, _ in self.field_values.items()}
        self.children = []
        self.set(**kwargs)

    def attributes(self):
        return self.field_values

    def set(self, **kwargs):
        for k, v in kwargs.items():
            if k in self.field_values:
                field_type = type(self.field_values[k])
                if field_type == datetime.datetime:
                    self.field_values[k] = parser.parse(v)
                elif field_type != str:
                    self.field_values[k] = field_type(v)
                else:
                    self.field_values[k] = v
                self.assigned[k] = True
        return self.complete()

    def complete(self):
        return all(self.assigned)

    def add_child(self, child):
        self.children.append(child)

    def unset_fields(self):
        unset = [x for x, y in self.assigned.items() if y is False]
        return unset

    def create_mapping(self):
        if self.complete() is False:
            msg = "The following fields have not been set: {}".format(", ".join(
                self.unset_fields()))
            raise ValueError(msg)


class AirSigmetXML2(XMLBaseClass):

    def __init__(self, **kwargs):
        self.field_values = {
            "raw_text": str(),
            "valid_time_from": datetime.datetime.min,
            "valid_time_to": datetime.datetime.min,
            "airsigmet_type": str(),
            "hazard__type": str(),
            "hazard__severity": str(),
            "altitude__min_ft_msl": int(),
            "altitude__max_ft_msl": int(),
            "movement_dir_degrees": int(),
            "movement_speed_kt": int(),
            "area__num_points": int(),
        }
        super().__init__(**kwargs)

    def create_mapping(self):
        if self.complete() is False:
            msg = "The following fields have not been set: {}".format(", ".join(
                self.unset_fields()))
            raise ValueError(msg)
        mapped = AirSigmet(**self.field_values)
        mapped.area = [x.create_mapping() for x in self.children]
        return mapped


class PointsXML2(XMLBaseClass):

    def __init__(self, **kwargs):
        self.field_values = {
            "latitude": float(),
            "longitude": float(),
        }

        super().__init__(**kwargs)

    def create_mapping(self):
        if self.complete() is False:
            msg = "The following fields have not been set: {}".format(", ".join(
                self.unset_fields()))
            raise ValueError(msg)
        return Points(**self.field_values)


class TafXML(XMLBaseClass):

    def __init__(self, **kwargs):
        self.field_values = {
            "raw_text": str(),
            "station_id": str(),
            "issue_time": datetime.datetime.min,
            "bulletin_time": datetime.datetime.min,
            "valid_time_from": datetime.datetime.min,
            "valid_time_to": datetime.datetime.min,
            "remarks": str(),
            "latitude": float(),
            "longitude": float(),
            "elevation_m": float(),
        }
        super().__init__(**kwargs)

    def create_mapping(self):
        if self.complete() is False:
            msg = "The following fields have not been set: {}".format(", ".join(
                self.unset_fields()))
            raise ValueError(msg)
        mapped = Taf(**self.field_values)
        mapped.forecast = [x.create_mapping() for x in self.children]
        return mapped


class ForecastXML(XMLBaseClass):

    def __init__(self, **kwargs):
        self.field_values = {
            "time_from": datetime.datetime.min,
            "time_to": datetime.datetime.min,
            "change_indicator": str(),
            "time_becoming": datetime.datetime.min,
            "probability": int(),
            "wind_dir_degrees": int(),
            "wind_speed_kt": int(),
            "wind_gust_kt": int(),
            "wind_shear_hgt_ft_agl": int(),
            "wind_shear_dir_degrees": int(),
            "wind_shear_speed_kt": int(),
            "visibility_statute_mi": float(),
            "altim_in_hg": float(),
            "vert_vis_ft": int(),
            "wx_string": str(),
            "not_decoded": str(),
        }
        super().__init__(**kwargs)

    def create_mapping(self):
        if self.complete() is False:
            msg = "The following fields have not been set: {}".format(", ".join(
                self.unset_fields()))
            raise ValueError(msg)
        mapped = Forecast(**self.field_values)
        for child in self.children:
            getattr(mapped, child.__attr_name__).append(child.create_mapping())
        return mapped


class SkyConditionXML(XMLBaseClass):
    __attr_name__ = "sky_condition"

    def __init__(self, **kwargs):
        self.field_values = {
            "sky_cover": str(),
            "cloud_base_ft_agl": int(),
            "cloud_type": str(),
        }
        super().__init__(**kwargs)

    def create_mapping(self):
        if self.complete() is False:
            msg = "The following fields have not been set: {}".format(", ".join(
                self.unset_fields()))
            raise ValueError(msg)
        return SkyCondition(**self.field_values)


class TurbulenceConditionXML(XMLBaseClass):
    __attr_name__ = "turbulence_condition"

    def __init__(self, **kwargs):
        self.field_values = {
            "turbulence_intensity": str(),
            "turbulence_min_alt_ft_agl": int(),
            "turbulence_max_alt_ft_agl": int(),
        }
        super().__init__(**kwargs)

    def create_mapping(self):
        if self.complete() is False:
            msg = "The following fields have not been set: {}".format(", ".join(
                self.unset_fields()))
            raise ValueError(msg)
        return TurbulenceCondition(**self.field_values)


class IcingConditionXML(XMLBaseClass):
    __attr_name__ = "icing_condition"

    def __init__(self, **kwargs):
        self.field_values = {
            "icing_intensity": str(),
            "icing_min_alt_ft_agl": int(),
            "icing_max_alt_ft_agl": int(),
        }
        super().__init__(**kwargs)

    def create_mapping(self):
        if self.complete() is False:
            msg = "The following fields have not been set: {}".format(", ".join(
                self.unset_fields()))
            raise ValueError(msg)
        return IcingCondition(**self.field_values)


class MetarXML(XMLBaseClass):

    def __init__(self, **kwargs):
        self.field_values = {
            "raw_text": str(),
            "station_id": str(),
            "observation_time": datetime.datetime.min,
            "latitude": float(),
            "longitude": float(),
            "temp_c": float(),
            "dewpoint_c": float(),
            "wind_dir_degrees": int(),
            "wind_speed_kt": int(),
            "wind_gust_kt": int(),
            "visibility_statute_mi": float(),
            "altim_in_hg": float(),
            "sea_level_pressure_mb": float(),
            "quality_control_flags": str(),
            "wx_string": str(),
            "flight_category": str(),
            "three_hr_pressure_tendency_mb": float(),
            "maxT_c": float(),
            "minT_c": float(),
            "maxT24hr_c": float(),
            "minT24hr_c": float(),
            "precip_in": float(),
            "pcp3hr_in": float(),
            "pcp6hr_in": float(),
            "pcp24hr_in": float(),
            "snow_in": float(),
            "vert_vis_ft": float(),
            "metar_type": str(),
            "elevation_m": float(),
        }
        super().__init__(**kwargs)

    def create_mapping(self):
        if self.complete() is False:
            msg = "The following fields have not been set: {}".format(", ".join(
                self.unset_fields()))
            raise ValueError(msg)
        mapped = Metar(**self.field_values)
        mapped.sky_condition = [x.create_mapping() for x in self.children]
        return mapped


class MetarSkyConditionXML(XMLBaseClass):
    __attr_name__ = "sky_condition"

    def __init__(self, **kwargs):
        self.field_values = {
            "sky_cover": str(),
            "cloud_base_ft_agl": int(),
            "cloud_type": str(),
        }
        super().__init__(**kwargs)

    def create_mapping(self):
        if self.complete() is False:
            msg = "The following fields have not been set: {}".format(", ".join(
                self.unset_fields()))
            raise ValueError(msg)
        return MetarSkyCondition(**self.field_values)
