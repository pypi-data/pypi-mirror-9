import configparser
from os.path import expanduser, join, isfile

__author__ = 'victor'


class ConfigLoader():
    SRCPATH = "srcpath"
    DESTPATH = "destpath"

    def __init__(self):
        self.userHome = expanduser("~")
        self.CONFIG_FILE = join(self.userHome, '.androidresr')
        self.config = configparser.RawConfigParser(allow_no_value=True)

        if not isfile(self.CONFIG_FILE):
            self.initFile()

        self.load()

    def load(self):
        if not isfile(self.CONFIG_FILE):
                raise RuntimeError('No config file (', self.CONFIG_FILE, ') found')
        self.config.readfp(open(self.CONFIG_FILE))

    def set(self, key, value):
        self.config.set('general', key, value)
        self.write()

    def get(self, key):
        try:
            return self.config.get("general", key)
        except configparser.NoOptionError:
            return None

    def initFile(self):
        self.config.add_section('general')
        self.write()

    def write(self):
        with open(self.CONFIG_FILE, 'w') as configfile:
            self.config.write(configfile)
