from config import Config

debug = False
dryrun = False
config = None


def init_config(configfile):
    global config

    config = Config(configfile)
