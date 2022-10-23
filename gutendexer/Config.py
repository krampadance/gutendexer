import os


class Config(object):
    # App related variables
    NAME = "gutendexer"
    VERSION = "0.1.0"

    # MONGODB related variables
    MONGO_URL = os.getenv(
        "MONGO_URL", "mongodb://api:apiPassword@127.0.0.1/gutendexer")
    DATABASE = os.getenv("DATABASE", "gutendexer")
