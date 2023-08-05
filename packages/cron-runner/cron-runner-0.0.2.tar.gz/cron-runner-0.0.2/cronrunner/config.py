import sys

import yaml


class Config():
    data = None
    config_file = None

    def __init__(self, config_file="../config.yaml"):
        self.config_file = config_file

    def load(self):
        try:
            with open(self.config_file, "r") as fh:
                self.data = yaml.load(fh.read())

        except Exception, e:
            print "Error reading config, %s" % e
            sys.exit(1)

    def get(self, key, default=None, section=None):
        if self.data is None:
            self.load()

        try:
            if section is not None:
                return self.data[section][key]

            return self.data[key]
        except Exception, e:
            return default

    def all(self):
        if self.data is None:
            self.load()

        return self.data