import ConfigParser

__author__ = 'Andriy Drozdyuk'


class ConfigurationService(object):
    def __init__(self, path):
        self.path = path

        self.config = ConfigParser.SafeConfigParser()
        self.config.read(path)

    @property
    def database_url(self):
        return self.config.get('database', 'url')