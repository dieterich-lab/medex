#!/usr/bin/env bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

FLASK_ENV=development
FLASK_APP=webserver.py
flask run --host=0.0.0.0
