"""
Config file handler for 'redis-client' section in jasmin.conf
"""

from jasmin.config.tools import ConfigFile
import logging

class RedisForJasminConfig(ConfigFile):
    "Config handler for 'redis-client' section"

    def __init__(self, config_file = None):
        ConfigFile.__init__(self, config_file)
        
        self.host = self._getint('redis-client', 'host', '127.0.0.1')
        self.port = self._getint('redis-client', 'port', 6379)
        self.dbid = self._getint('redis-client', 'dbid', '1')
        self.password = self._getint('redis-client', 'password', None)
        self.poolsize = self._getint('redis-client', 'poolsize', 10)
        
        self.log_level = logging.getLevelName(self._get('redis-client', 'log_level', 'INFO'))
        self.log_file = self._get('redis-client', 'log_file', '/var/log/jasmin/redis-client.log')
        self.log_format = self._get('redis-client', 'log_format', '%(asctime)s %(levelname)-8s %(process)d %(message)s')
        self.log_date_format = self._get('redis-client', 'log_date_format', '%Y-%m-%d %H:%M:%S')
