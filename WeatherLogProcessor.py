""" WeatherLogProcessor
Processes a tsv file and provides functions to get reports
"""
import json
import csv

from maxminddb import open_database
from OpenWeatherMap import OpenWeatherMap
from WeatherCache import WeatherCache
from ErrorReport import ErrorReport
from TimeUtils import TimeUtils

class WeatherLogProcessor(object):
    """Used for reading, processing a tsv log file
    """
    def __init__(self, config_file, flush_cache=False, verbose=False):
        self.max_forecasts = []
        self.lines_processed = 0
        self.delimiter = '\t'
        with open(config_file) as conf_file:
            config = json.load(conf_file)

        self.error_report = ErrorReport()
        self.time_utils = TimeUtils()

        self.verbose = verbose
        self.geo_precision = config['log_processor']['geo_precision']
        self.geoip_db = open_database(config['geoip_db']['file'])

        self.weather_api = OpenWeatherMap(api_key=config['weather_api']['api_key'],
                                          units=config['weather_api']['units'])

        self.weather_cache = WeatherCache(host=config['cache']['host'],
                                          port=config['cache']['port'],
                                          redis_key_expiry_secs=config['cache']['key_expiry_secs']
                                         )
        if flush_cache:
            self.weather_cache.flush()


    def _round_to(self, val):
        """Returns a value rounded to the precision value"""
        correction = 0.5 if val >= 0 else -0.5
        return int(val/self.geo_precision+correction) * self.geo_precision

    def get_tomorrows_max(self, latitude, longitude):
        """Returns the forecast max for tomorrow given latitude and longitude"""
        start_of_tomorrow = self.time_utils.get_start_of_tomorrow_utc()
        end_of_tomorrow = self.time_utils.get_end_of_tomorrow_utc()
        temperature = self.weather_cache.get_forecast_max(latitude=latitude,
                                                          longitude=longitude,
                                                          forecast_date=start_of_tomorrow)

        if temperature:
            if self.verbose:
                print("retrieved from cache")
        else:
            temperature = self.weather_api.get_geo_max_temperature(latitude=latitude,
                                                                   longitude=longitude,
                                                                   start=start_of_tomorrow,
                                                                   end=end_of_tomorrow)
            if self.verbose:
                print("retrieved from api call")
            self.weather_cache.set_forecast_max(latitude=latitude,
                                                longitude=longitude,
                                                forecast_date=start_of_tomorrow,
                                                temperature=temperature)
        return temperature

    def process_tsv(self, input_file):
        """Loops through values in tsv looking in forecast max in cache first
        Then does a api call if value is not in cache"""

        with open(input_file) as tsvfile:
            reader = csv.reader(tsvfile, delimiter=self.delimiter)
            line_number = 0
            for row in reader:
                line_number = line_number + 1
                try:
                    temperature = None
                    ip_address = row[23]
                    geoip_result = self.geoip_db.get(ip_address)
                    if geoip_result is None:
                        raise Exception("No entry found in geodb")
                    else:
                        latitude = self._round_to(val=geoip_result['location']['latitude'])

                        longitude = self._round_to(val=geoip_result['location']['longitude'])

                        temperature = self.get_tomorrows_max(latitude=latitude,
                                                             longitude=longitude)
                        self.max_forecasts.append(temperature)

                except Exception as e:
                    self.error_report.add_error(error_str=str(e),
                                                line_number=line_number)

            if len(self.max_forecasts) == 0:
                raise Exception("No forecasts returned")

            self.lines_processed = line_number
            self.max_forecasts = sorted(self.max_forecasts)


    def create_histogram_tsv(self, number_of_buckets, output_file):
        """ Creates the histogram tsv file once all max temperatures is created"""

        if len(self.max_forecasts) < number_of_buckets:
            number_of_buckets = len(self.max_forecasts)

        bucket_size = (self.max_forecasts[-1] - self.max_forecasts[0]) / number_of_buckets
        bucket_min = self.max_forecasts[0]
        bucket_max = self.max_forecasts[0] + bucket_size
        count = 0

        with open(output_file, 'w') as file:
            filewriter = csv.writer(file,
                                    delimiter=self.delimiter,
                                    quoting=csv.QUOTE_MINIMAL,
                                    quotechar='|'
                                   )
            filewriter.writerow(['bucketMin', 'bucketMax', 'count'])
            for forecast in self.max_forecasts:
                if forecast <= bucket_max:
                    count = count + 1
                else:
                    filewriter.writerow([round(bucket_min, 2),
                                         round(bucket_max, 2),
                                         count])
                    count = 1
                    bucket_min = bucket_max
                    bucket_max = bucket_max + bucket_size

            filewriter.writerow([round(bucket_min, 2),
                                 round(bucket_max, 2),
                                 count])

    def print_error_report(self):
        errors = self.error_report.get_errors()
        if errors:
            print("ERROR REPORT:")
            for key, error in errors.items():
                print("ERROR TYPE: {}".format(key))
                print("count: {} out of {} lines processed".format(error['count'], self.lines_processed))
                print("error happened on lines: {}".format(error['lines']))
                print("")
        else:
            print("No errors found.")

    def close(self):
        self.geoip_db.close()
