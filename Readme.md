# Devops Weather Exercise - The trade desk

Reads tsv file and creates a tsv histogram file containing histogram bins
of forecasted high temperatures of the locations discovered in the input log.

## Getting Started

### Prerequisites

This solution requires docker, python 2.7 and pip

To install docker, refer:
https://docs.docker.com/install/

to install python 3.7.0, refer to:
https://www.python.org/downloads/

to install pip:
https://pip.pypa.io/en/stable/installing/

you will need to get an api key for OpenWeatherMap.org
To do so, sign up to: https://openweathermap.org/ and retrieve your api key

### Download maxmind geoip database

Download: http://geolite.maxmind.com/download/geoip/database/GeoLite2-City.tar.gz
Expand it. Copy GeoLite2-City.mmdb into ./data/GeoLite2-City.mmdb


### Startup Redis via docker

The solution uses Redis cache as it expires keys quite nicely.

```
docker run --name redis -d -p 6379:6379 redis:4
```

### Install required python packages

The following python packages are required.
- argparse
- redis
- python-geoip
- pytz
- tzlocal

```
pip install --user argparse
pip install --user redis
pip install --user python-geoip
pip install --user pytz
pip install --user tzlocal
```

### Config file

A configuration file is provided in config/weather.json
At the very minimum, you will need to update weather_api.api_key with api key
obtained from http://openweathermap.org
Attributes are:

```
weather_api.api_key: your weather api_key from http://openweathermap.org
weather_api.units: forecast units. eg: imperial or metric
cache.host: the host where the cache is living on
cache.port: the port the cache is listening on
geoip_db: the location of the GeoLite2-City.mmdb file
log_processor.geo_precision: the rounding number for longitude and latitude.
  eg: if the value 0.2; and longitude to lookup is 100.222222, it will be rounded to 100.2
```


## Usage
Example:
  ./main.py --inputFile ./input/devops_coding_input_log1.tsv --outputFile out.tsv -H 10

 Attributes:
    --inputFile, -i: The input file tsv file

    --outputFile, -o: The output file

    --histogramBuckets, -H: Number of histogram buckets

    --configFile, -c: location of the configuration file

    --flushCache: flushes the cache. Optional. Good for testing

    --verbose, -v: prints out where the value was retrieved from - API or Cache