from datetime import date

import numpy as np

from ds_weather_api import *


class WeatherFeatureExtractor:
    date_to_hours: dict = None
    data_loaded: bool = False

    DATA_PATH = '../Data/WeatherData_May2018-May2019.bin'

    @classmethod
    def load_data(cls):

        class CustomUnpickler(pickle.Unpickler):
            def find_class(self, module, name):
                if module == "__main__":
                    module = 'ds_weather_api'
                return super().find_class(module, name)

        with open(cls.DATA_PATH, 'rb') as f:
            weather_data = CustomUnpickler(f).load()

        # Change Format
        cls.date_to_hour = {}
        date_to_hours = WeatherFeatureExtractor.date_to_hours
        for data in weather_data:
            hourly_data = data[WeatherReportType.Hourly]

            for val in data[WeatherReportType.Daily].values():
                daily = val
                break

            hours = sorted(hourly_data.keys())
            for hour in hours:
                dt = hour.date()
                if dt not in date_to_hours:
                    date_to_hours[dt] = {}
                date_to_hours[dt][hour.hour] = hourly_data[hour].extend_with(daily)

        # Imputate data from previous hour
        prev_good_hour_value = None
        prev_good_temperature = None
        for dt in date_to_hours:
            for hour in range(24):
                if hour not in date_to_hours[dt]:
                    date_to_hours[dt][hour] = prev_good_hour_value
                else:
                    prev_good_hour_value = date_to_hours[dt][hour]
                    if prev_good_hour_value is None:
                        continue
                    if prev_good_hour_value.temperature is not None:
                        prev_good_temperature = prev_good_hour_value.temperature
                    else:
                        prev_good_hour_value.temperature = prev_good_temperature

    @classmethod
    def get_feature_dict(cls, date_, time):

        if not cls.data_loaded:
            cls.load_data()

        date_to_hours = cls.date_to_hours

        dt = date.fromisoformat(date_)
        hour = int(np.round(time / 100.))

        ret = {}
        for attr_name in ['weather_label', 'precipitation_intensity', 'precipitation_probability', 'visibility',
                          'cloud_cover', 'humidity', 'wind_bearing', 'wind_speed', 'uv_index', 'temperature',
                          'moon_phase', 'sunrise_time', 'sunset_time', 'dew_point', 'pressure']:

            if dt not in date_to_hours or hour not in date_to_hours[dt]:
                ret[attr_name] = np.nan
            else:
                ret[attr_name] = date_to_hours[dt][hour].__getattribute__(attr_name)

        return ret


def get_weather_features_dict(date, time):
    """

    :param date: the 'FL_DATE' column
    :param time: the 'HOUR' column
    :return: rtn_dict: labels = {'weather_label', 'precipitation_intensity', 'precipitation_probability', 'visibility',
                          'cloud_cover', 'humidity', 'wind_bearing', 'wind_speed', 'uv_index', 'temperature',
                          'moon_phase', 'sunrise_time', 'sunset_time', 'dew_point', 'pressure'}
    """

    return WeatherFeatureExtractor.get_feature_dict(date, time)
