"""Class to handle connections to https://openweathermap.org/api
"""
import datetime
import math
import requests
import pytz

class OpenWeatherMapEndpoints:
    """Static values for api lookups with openweathermap"""
    FORECAST_API_URI = 'http://api.openweathermap.org/data/2.5/forecast'
    GEO_FORECAST_QUERY_STRING = '?lat=[[lat]]&lon=[[lon]]' \
                                +'&cnt=[[count]]' \
                                + '&units=[[unit_type]]' \
                                +'&APPID=[[api_key]]'

class OpenWeatherMap(object):
    """Class object to connect and make calls to https://openweathermap.org/api
    """

    def __init__(self, api_key, units):
        """
        Args:
            api_key (str): the api key to connect
            units (str): the units type. eg: imperial or metric
        """
        self.api_key = api_key
        self.units = units
        self.geo_forecast_uri = "%s%s" % (OpenWeatherMapEndpoints.FORECAST_API_URI,
                                          OpenWeatherMapEndpoints.GEO_FORECAST_QUERY_STRING)
        self.geo_forecast_uri = self.geo_forecast_uri.replace('[[api_key]]', self.api_key)
        self.geo_forecast_uri = self.geo_forecast_uri.replace('[[unit_type]]', self.units)


    def _get_geo_uri(self, latitude, longitude, number_of_results):
        """Returns the URI for geo location lookup"""

        uri = self.geo_forecast_uri
        uri = uri.replace('[[lat]]', str(latitude))
        uri = uri.replace('[[lon]]', str(longitude))
        uri = uri.replace('[[count]]', str(number_of_results))
        return uri

    @classmethod
    def _get_number_of_results_for_forecast(cls, date):
        """Returns the number of results as the api returns forecast in 3 hour increments"""
        utcnow = datetime.datetime.utcnow()
        end_tznative = date.replace(tzinfo=None)
        number_of_results = (end_tznative - utcnow).total_seconds() / 3600 / 3
        return str(int(math.ceil(number_of_results)))


    def get_geo_weather_forecast(self, latitude, longitude, number_of_results):
        """Returns the forecast
        Args:
            latitude (float): the geo latitude
            longitude (float): the geo longitude
            number_of_results (float): number of results to be returned from api
        """

        uri = self._get_geo_uri(latitude, longitude, number_of_results)
        result = requests.get(uri)
        if result.status_code != 200:
            raise Exception("HTTP error code was %s" % result.status_code)
        return result.json()


    def get_geo_max_temperature(self, latitude, longitude, start, end):
        """Returns the forecast max for a location between 2 dates
        Args:
            latitude (float): the geo latitude
            longitude (float): the geo longitude
            start (datetime): the start datetime for lookup
            end (datetime): the end datetime for lookup
        """
        max_temperature = None
        number_of_results = self._get_number_of_results_for_forecast(end)

        forecast_data = self.get_geo_weather_forecast(latitude,
                                                      longitude,
                                                      number_of_results)
        for result in forecast_data['list']:
            result_date = datetime.datetime.strptime(result['dt_txt'], "%Y-%m-%d %H:%M:%S")
            result_date = result_date.replace(tzinfo=pytz.UTC)

            if result_date > start and result_date < end:
                if (max_temperature is None) or (float(result['main']['temp_max']) > max_temperature):
                    max_temperature = result['main']['temp_max']
        return max_temperature
