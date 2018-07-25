""" Weather Cache handler
At the moment it connects to Redis unsecurely. In prod, this will be over SSL
"""
import redis

class WeatherCache(object):
    """ Connection to Redis"""
    def __init__(self, host, port, redis_key_expiry_secs=86400, password=None):
        """
        Args:
            host (str): the uri for the host. eg: localhost
            port (int): the port number redis listening on
            password (str): the password to connect to redis
            redis_key_expiry_secs (int): how long a key will live in redisself.
                default is 1 day
        """

        self.redis_key_expiry_secs = redis_key_expiry_secs
        self.redis_db = redis.Redis(
            host=host,
            port=port,
            password=password
        )

    def get_forecast_max(self, latitude, longitude, forecast_date):
        """ Returns the forecast max based on a date, latitude and longitude"""
        key = "%s%s-%s", (str(latitude), str(longitude), str(forecast_date))
        val = self.redis_db.get(key)
        if val:
            return float(val)
        else:
            return None

    def set_forecast_max(self, latitude, longitude, forecast_date, temperature):
        """ Sets the forecast max based on a date, latitude and longitude"""
        key = "%s%s-%s", (str(latitude), str(longitude), str(forecast_date))
        self.redis_db.set(key, temperature)
        self.redis_db.expire(key, self.redis_key_expiry_secs)


    def flush(self):
        """ Flushes the entire redisdb. Good for testing """
        self.redis_db.flushdb()
