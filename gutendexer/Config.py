import os


class Config(object):
    # App related variables
    NAME = "gutendexer"
    VERSION = "0.1.0"

    # MONGODB related variables
    MONGO_HOST = os.getenv(
        "MONGO_HOST", "127.0.0.1")
    MONGO_USER = os.getenv("MONGO_USER", "api")
    MONGO_PASSWORD = os.getenv("MONGO_PASSWORD", "apiPassword")

    DATABASE = os.getenv("DATABASE", "gutendexer")

    # Gutendex related variables
    GUTENDEX_URL = os.getenv("GUTENDEX_URL", "http://gutendex.com/books")
