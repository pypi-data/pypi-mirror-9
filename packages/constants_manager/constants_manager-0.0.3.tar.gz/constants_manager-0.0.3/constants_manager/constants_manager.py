try:
    import ConfigParser as configparser
except ImportError:
    import configparser
import os
import logging


class ConstantsManager():
    def __init__(self, config_file_name='constants.ini', constants_name='ENV'):
        self.config_file_name = config_file_name
        self.constants_name = constants_name

    def __get_environment(self):
        __env_default = 'DEFAULT'
        __constants_name = self.constants_name
        __env = os.environ[__constants_name] if __constants_name in os.environ else __env_default
        return __env

    def get(self, key):
        config = configparser.RawConfigParser()
        config.optionxform = str
        config.read(self.config_file_name)
        __env = self.__get_environment()
        __val = config.get(__env, key)
        return __val

