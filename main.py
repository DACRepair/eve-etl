#!/usr/bin/env python3

from eve_etl.Common.Config import config
from eve_etl.web import flask

if __name__ == "__main__":
    flask.run(host=config.get("AuthServer", "host"), port=config.getint("AuthServer", "port"))
