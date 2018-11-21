API GUIDE
=========
calculations
------------
  * Description: Get various weather data for a particular flight.
  * Arguments: Takes 3 arguments:
    - Weather type:

      * airsigmet: Airmet or Sigmet along the flight route.

      * taf: TAFs of departure and arrival airports for schedule departure and arrival times.

      * metar: Most recent METARs for both departure and arrival airports.

    - Flight number

      * Three letter airline identifier and flight number

      * Example: JBU135

    - Departure time

      * Scheduled departure time for the flight, in POSIX Epoch format.

  * Example::

      python -m src.calculations taf JBU135 1542697200

  * Returned data:

    * Data is returned in JSON format.

    * Airsigmets will be a list of Airmets and Sigmets along the flight route.

    * TAFs will be a list of the most recent valid TAFs for the scheduled departure and scheduled arrival.

    * METARs will be a list of 2 items:

      * The most recent metar for the departure airport.

      * The most recent metar for the arrival airport.

    * An empty list returned means there was no weather data meeting the criteria.

      * For Airsigmets, there was no airsigmet along the flight route.

      * For TAFs, there was no current TAF for that airport at the scheduled time.

Examples
--------

**Example taf output**::

    [
      {
        "bulletin_time": 1542698760.0,
        "remarks": "",
        "elevation_m": 278.0,
        "raw_text": "TAF AMD KRDR 200218Z 2002/2108 20009KT 9999 BKN150 QNH3023INS BECMG 2005/2006 20009KT 9999 FEW050 BKN140 QNH2998INS BECMG 2010/2011 21009KT 9000 -SN BKN020 BKN070 620202 620708 QNH2994INS BECMG 2011/2013 24012KT 8000 -SN OVC015 620159 510202 QNH2992INS BECMG 2016/2017 34012G25KT 9999 NSW OVC015 620159 510202 QNH2999INS BECMG 2018/2019 34012G20KT 9999 BKN020 620204 QNH3001INS BECMG 2023/2024 36012KT 9999 SCT025 BKN070 620705 QNH3016INS TX00/2018Z TNM19/2003Z",
        "valid_time_from": 1542697200.0,
        "issue_time": 1542698280.0,
        "longitude": -97.4,
        "latitude": 47.97,
        "forecast": [
          {
            "probability": 0,
            "wind_speed_kt": 9,
            "vert_vis_ft": 0,
            "time_becoming": -62135576869.0,
            "wind_gust_kt": 0,
            "sky_condition": [
              {
                "cloud_type": "",
                "cloud_base_ft_agl": 15000,
                "parent_id": 82,
                "sky_cover": "BKN"
              }
            ],
            "time_to": -62135576869.0,
            "wx_string": "",
            "not_decoded": "",
            "turbulences_condition": [],
            "wind_shear_hgt_ft_agl": 0,
            "icing_condition": [],
            "parent_id": 22,
            "change_indicator": "",
            "altim_in_hg": 30.2362,
            "wind_dir_degrees": 200,
            "wind_shear_speed_kt": 0,
            "visibility_statute_mi": 6.21,
            "time_from": -62135576869.0,
            "wind_shear_dir_degrees": 0
          },
          {
            "probability": 0,
            "wind_speed_kt": 9,
            "vert_vis_ft": 0,
            "time_becoming": 1542711600.0,
            "wind_gust_kt": 0,
            "sky_condition": [
              {
                "cloud_type": "",
                "cloud_base_ft_agl": 5000,
                "parent_id": 83,
                "sky_cover": "FEW"
              },
              {
                "cloud_type": "",
                "cloud_base_ft_agl": 14000,
                "parent_id": 83,
                "sky_cover": "BKN"
              }
            ],
            "time_to": -62135576869.0,
            "wx_string": "",
            "not_decoded": "",
            "turbulences_condition": [],
            "wind_shear_hgt_ft_agl": 0,
            "icing_condition": [],
            "parent_id": 22,
            "change_indicator": "BECMG",
            "altim_in_hg": 29.9705,
            "wind_dir_degrees": 200,
            "wind_shear_speed_kt": 0,
            "visibility_statute_mi": 6.21,
            "time_from": -62135576869.0,
            "wind_shear_dir_degrees": 0
          },
          {
            "probability": 0,
            "wind_speed_kt": 9,
            "vert_vis_ft": 0,
            "time_becoming": 1542729600.0,
            "wind_gust_kt": 0,
            "sky_condition": [
              {
                "cloud_type": "",
                "cloud_base_ft_agl": 2000,
                "parent_id": 84,
                "sky_cover": "BKN"
              },
              {
                "cloud_type": "",
                "cloud_base_ft_agl": 7000,
                "parent_id": 84,
                "sky_cover": "BKN"
              }
            ],
            "time_to": -62135576869.0,
            "wx_string": "-SN",
            "not_decoded": "",
            "turbulences_condition": [],
            "wind_shear_hgt_ft_agl": 0,
            "icing_condition": [
              {
                "icing_max_alt_ft_agl": 4000,
                "icing_min_alt_ft_agl": 2000,
                "parent_id": 84,
                "icing_intensity": "2"
              },
              {
                "icing_max_alt_ft_agl": 15000,
                "icing_min_alt_ft_agl": 7000,
                "parent_id": 84,
                "icing_intensity": "2"
              }
            ],
            "parent_id": 22,
            "change_indicator": "BECMG",
            "altim_in_hg": 29.9409,
            "wind_dir_degrees": 210,
            "wind_shear_speed_kt": 0,
            "visibility_statute_mi": 5.59,
            "time_from": -62135576869.0,
            "wind_shear_dir_degrees": 0
          },
          {
            "probability": 0,
            "wind_speed_kt": 12,
            "vert_vis_ft": 0,
            "time_becoming": 1542736800.0,
            "wind_gust_kt": 0,
            "sky_condition": [
              {
                "cloud_type": "",
                "cloud_base_ft_agl": 1500,
                "parent_id": 85,
                "sky_cover": "OVC"
              }
            ],
            "time_to": -62135576869.0,
            "wx_string": "-SN",
            "not_decoded": "",
            "turbulences_condition": [],
            "wind_shear_hgt_ft_agl": 0,
            "icing_condition": [
              {
                "icing_max_alt_ft_agl": 10500,
                "icing_min_alt_ft_agl": 1500,
                "parent_id": 85,
                "icing_intensity": "2"
              }
            ],
            "parent_id": 22,
            "change_indicator": "BECMG",
            "altim_in_hg": 29.9114,
            "wind_dir_degrees": 240,
            "wind_shear_speed_kt": 0,
            "visibility_statute_mi": 4.97,
            "time_from": -62135576869.0,
            "wind_shear_dir_degrees": 0
          },
          {
            "probability": 0,
            "wind_speed_kt": 12,
            "vert_vis_ft": 0,
            "time_becoming": 1542751200.0,
            "wind_gust_kt": 25,
            "sky_condition": [
              {
                "cloud_type": "",
                "cloud_base_ft_agl": 1500,
                "parent_id": 86,
                "sky_cover": "OVC"
              }
            ],
            "time_to": -62135576869.0,
            "wx_string": "NSW",
            "not_decoded": "",
            "turbulences_condition": [],
            "wind_shear_hgt_ft_agl": 0,
            "icing_condition": [
              {
                "icing_max_alt_ft_agl": 10500,
                "icing_min_alt_ft_agl": 1500,
                "parent_id": 86,
                "icing_intensity": "2"
              }
            ],
            "parent_id": 22,
            "change_indicator": "BECMG",
            "altim_in_hg": 30.0,
            "wind_dir_degrees": 340,
            "wind_shear_speed_kt": 0,
            "visibility_statute_mi": 6.21,
            "time_from": -62135576869.0,
            "wind_shear_dir_degrees": 0
          },
          {
            "probability": 0,
            "wind_speed_kt": 12,
            "vert_vis_ft": 0,
            "time_becoming": 1542758400.0,
            "wind_gust_kt": 20,
            "sky_condition": [
              {
                "cloud_type": "",
                "cloud_base_ft_agl": 2000,
                "parent_id": 87,
                "sky_cover": "BKN"
              }
            ],
            "time_to": -62135576869.0,
            "wx_string": "NSW",
            "not_decoded": "",
            "turbulences_condition": [],
            "wind_shear_hgt_ft_agl": 0,
            "icing_condition": [
              {
                "icing_max_alt_ft_agl": 6000,
                "icing_min_alt_ft_agl": 2000,
                "parent_id": 87,
                "icing_intensity": "2"
              }
            ],
            "parent_id": 22,
            "change_indicator": "BECMG",
            "altim_in_hg": 30.0,
            "wind_dir_degrees": 340,
            "wind_shear_speed_kt": 0,
            "visibility_statute_mi": 6.21,
            "time_from": -62135576869.0,
            "wind_shear_dir_degrees": 0
          },
          {
            "probability": 0,
            "wind_speed_kt": 12,
            "vert_vis_ft": 0,
            "time_becoming": 1542776400.0,
            "wind_gust_kt": 0,
            "sky_condition": [
              {
                "cloud_type": "",
                "cloud_base_ft_agl": 2500,
                "parent_id": 88,
                "sky_cover": "SCT"
              },
              {
                "cloud_type": "",
                "cloud_base_ft_agl": 7000,
                "parent_id": 88,
                "sky_cover": "BKN"
              }
            ],
            "time_to": -62135576869.0,
            "wx_string": "NSW",
            "not_decoded": "",
            "turbulences_condition": [],
            "wind_shear_hgt_ft_agl": 0,
            "icing_condition": [
              {
                "icing_max_alt_ft_agl": 12000,
                "icing_min_alt_ft_agl": 7000,
                "parent_id": 88,
                "icing_intensity": "2"
              }
            ],
            "parent_id": 22,
            "change_indicator": "BECMG",
            "altim_in_hg": 30.1476,
            "wind_dir_degrees": 360,
            "wind_shear_speed_kt": 0,
            "visibility_statute_mi": 6.21,
            "time_from": -62135576869.0,
            "wind_shear_dir_degrees": 0
          }
        ],
        "station_id": "KRDR",
        "valid_time_to": 1542805200.0
      },
      {
        "bulletin_time": 1542698640.0,
        "remarks": "AMD",
        "elevation_m": 241.0,
        "raw_text": "KIND 200224Z 2002/2106 27007KT P6SM BKN015 OVC130",
        "valid_time_from": 1542697200.0,
        "issue_time": 1542698640.0,
        "longitude": -86.3,
        "latitude": 39.72,
        "forecast": [
          {
            "probability": 0,
            "wind_speed_kt": 7,
            "vert_vis_ft": 0,
            "time_becoming": -62135576869.0,
            "wind_gust_kt": 0,
            "sky_condition": [
              {
                "cloud_type": "",
                "cloud_base_ft_agl": 1500,
                "parent_id": 60,
                "sky_cover": "BKN"
              },
              {
                "cloud_type": "",
                "cloud_base_ft_agl": 13000,
                "parent_id": 60,
                "sky_cover": "OVC"
              }
            ],
            "time_to": -62135576869.0,
            "wx_string": "",
            "not_decoded": "",
            "turbulences_condition": [],
            "wind_shear_hgt_ft_agl": 0,
            "icing_condition": [],
            "parent_id": 16,
            "change_indicator": "",
            "altim_in_hg": 0.0,
            "wind_dir_degrees": 270,
            "wind_shear_speed_kt": 0,
            "visibility_statute_mi": 6.21,
            "time_from": -62135576869.0,
            "wind_shear_dir_degrees": 0
          }
        ],
        "station_id": "KIND",
        "valid_time_to": 1542798000.0
      }
    ]

End of example.
