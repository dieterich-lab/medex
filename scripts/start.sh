#!/usr/bin/env bash

script_dir=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
base_dir=$(dirname "$script_dir")

# enviroment variables
export FLASK_DEBUG=1
export FLASK_APP=webserver.py

export POSTGRES_USER=test
export POSTGRES_PASSWORD=test
export POSTGRES_DB=example
export POSTGRES_PORT=5429
export POSTGRES_HOST=localhost

export FRONTEND_PATH="$base_dir/medex_client/dist"

# run flask
flask run
