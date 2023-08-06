__author__ = 'matthewcalabro'

import ConfigParser
import io


class Configuration:

    __configuration_file = 'onpage_configuration.cfg'

    def __init__(self):
        pass

    def __get_configuration_file(self):
            configuration = ConfigParser.RawConfigParser()
            configuration.read(self.__configuration_file)
            return configuration

    def get_enterprise_from_configuration(self):
        enterprise_name = ""

        try:
            enterprise_name = self.__get_configuration_file().get("credentials", "enterprise")
        except ConfigParser.NoSectionError:
            print("configuration for enterprise not found")
        except ConfigParser.NoOptionError:
            print("enterprise option not found in configuration file")

        return enterprise_name

    def get_token_from_configuration(self):
        token = ""

        try:
            token = self.__get_configuration_file().get("credentials", "token")
        except ConfigParser.NoSectionError:
            print("configuration for enterprise not found")
        except ConfigParser.NoOptionError:
            print("token option not found in configuration file")

        return token

    def get_uri_from_configuration(self):
        uri = ""

        try:
            uri = self.__get_configuration_file().get("settings", "uri")
        except ConfigParser.NoSectionError:
            print("settings for enterprise not found")
        except ConfigParser.NoOptionError:
            print("uri option not found in configuration file")

        return uri