# MedEx - Medical Data Explorer

This project provides a dashboard tool to allow a quick exploratory data analysis of datasets.
It was developed to allow a quick insight into our medical research-data-warehouse without the need of knowing how to use SQL or programming languages. 
However, it is not limited to clinical data, but can be used to do exploratory data analysis on many kind of datasets. 

## Production Setup

### Overview

The recommended way to run MedEx in production is via Docker. To do so
you will need first a docker image. You may build that elsewhere and
copy it over e.g. via a Docker Registry to your production server.

### Requirements

Building the Docker image:

* [Docker-CE](https://docs.docker.com/install/) >= 18.09.07
* NodeJS with npm

Running the docker image:

* docker-compose

### Building the Image

1. Get a copy of the MedEx repository.

2. Build the docker image

3. Tag the image:

        docker tag <ID from above command> medex:latest

### Running the Docker Image

1. Create your docker-compose.yml in based on the 
   one in the folder ./examples. Make sure that file has restrictive 
   permissions because it contains sensitive information - most importantly
   the database password. If you plan to run multiple instances on the same
   server, make sure that  the public ports for both the applications and
   the databases don't collide.

   In the default configuration the database will be destroyed and imported
   again everytime the database container is created. For large datasets
   that may be undesirable. The easiest way to change that is to create
   bind mount in the database container's definition. A docker volume may
   work too.

2. Tag the docker image. The tag needs to match the one you use in your
   docker-compose.yml:

        docker tag <ID of the image you just build> medex:latest

3. Create a folder 'import' in the same directory your docker-compose.yml
   file resides. Place here your data:
   * entities.csv:
     * A CSV file defining the types of data (entities) may have.
     * The header line must at least contain the following fields: key,type
     * The type may be 'String' for categorical data or 'Double' for numerical
       data. The type 'Date' is also allowed but not fully implemented.
   * dataset.csv:
     * A CSV file, which contains the actual data.
     * The header line must include at least these: patient_id,key,value
     * The 'key' field must contain values defined in 'entities.csv'.
     * The allowed values depend on the entities type. 'Date' values must
       be in format 'YYYY-MM-DD'.
     * The following optional fields may be included: case_id, measurement,
       date (YYYY-MM-DD), time (HH:MM:SS).

4. Bring up the containers:

        docker-compose up -d

On the initial run the database will be loaded. Dependending on the size of
the data that may take some time. Use "docker log *container-ID*"
to observe that. After the successful load a marker file will be created.
If the input data is changed on the next start of the container a new import
will be done.

## Upgrade

MedEx 1.0 and newer used Alembic to track the version of database schema.
When upgrading from older versions it is recommended to recreate the database
from scratch.

Some development versions MedEx recommended the use of Docker Swarm via "docker stack".
This approach is not considered reasonable anymore because of the incomplete
support of the Docker Compose File format. Most notable the shared memory
configuration is only possible with obscure workarounds. For details see:

* https://github.com/moby/moby/issues/26714
* https://stackoverflow.com/questions/55416904/increase-dev-shm-in-docker-container-in-swarm-environment-docker-stack-deploy

As a consequence the recommended method to run MedEx is now using "docker compose".

## Development Setup

### Requirements

* Linux (maybe MacOS works too)
* [Python](https://www.python.org/) >= 3.8
* [Docker-CE](https://docs.docker.com/install/) >= 18.09.07
* [NodeJS](https://nodejs.org) with npm>= 14.21
* Recommended: A Python IDE e.g. PyCharm - PyCharm Professional preferred due to
  the better JavaScript support.

### Installation

1. Create a Python venv with your preferred method and activate it:
   * E.g. using your IDE's mechanism (PyCharm)
   * or manually:

         python3 -m venv /where/ever/my/venv
         . /where/ever/my/venv/bin/activate

2. Install pipenv in this venv:

       pip install pipenv

3. Go to your MeDex working copy.

4. Install both the run-time and the development dependencies:

       pipenv install -e .
       pipenv install --dev
       npm install --save-dev

5. Bring up a database. You may use the configuration under ./examples for that:

       ( cd examples/docker_database_only && docker-compose up -d )

6. Bring up the backend DEV server:

       ./scripts/start.sh

7. Run the frontend DEV server:

       ( cd medex_client && npm run dev )

To test connect to the frontend DEV server http://localhost:5173.

**Important:** Due to an incompatibility of typia and vite we separately compile
the validators defined in medex_client/typia_src to create medex_client/src/typia.
That is done automatically when starting "npm run dev" or "npm run build".
This must be triggered after every change in medex_client/typia_src e.g. by
restarting the frontend dev server or by manually running in medex_client:

        npx typia generate --input typia_src/typia --output src/typia --project tsconfig.node.json

**Hint for PyCharm users:** To use the PyCharm's debugger easily you may prefer
to create "Run Configuration" in PyCharm instead of using 'start.sh'. To do that,
you need to copy the environment variables from that script to the run configuration.

### File System Layout

* Backend (Python 3)
  * webserver.py: Flask applikation wrapper
  * medex: Python packages
  * tests: Unit Tests
  * integration_tests: Tests for Postgres specific functionality - use Docker container with Postgres database
  * schema: Alemic database migration scripts - must be in sync wit medex/database_schema.py
* Frontend (TypeScript)
  * medex_client/src: Actual TypeScript Code
  * medex_client/src/typia: Automatically geneated validators - don't touch.
  * medex_client/typia_src: Some data structures and there validation routines. They are used to automatically
    generate medex_client/src/typia.
  * build: Directory with intermediate code generated by TypeScript
  * static/images: Images - mostly for the Tutorial page
  * static/js: Filled by the rollup bundler using the content of the build directory

### Environment Variables

The following environment variables define the connection to the database:

* _POSTGRES_USER_: Database user, e.g.: medex
* _POSTGRES_PASSWORD_: The password
* _POSTGRES_DB_: The name of the database., e.g.: medex 
* _POSTGRES_PORT_: The port of the database. Inside a docker-compose setup, just always use default port 5432, because the whole setup is isolated in its own network. Otherwise, you might want to use a different port to avoid collisions with other Postgres instances.
* _POSTGRES_HOST_: The host name. In the a docker-compose setup it should be the internal name of the service (database_medex, if you stick to the supplied example).

To get nicer status messages you may want to disable buffering on Python's output file handle:

* _PYTHONUNBUFFERED_: Set to '1' disable buffering.

To ensure that backend serves the bundled frontend file you may have set:

* _FRONTEND_PATH_: The default is '/app/static', which is just what the Docker container needs. If you want to test bundled files instead of yusing the vite DEV server, you may point it to 'medex_client/dist'. This directory will be created/updated if you run `npm run build` in the `medex_client` folder.

## Data Import

Data is imported from the 'import' directory during the start of the application,
when it seems necessary (e.g. first run or after change of the input files).

For details see: https://github.com/dieterich-lab/medex/blob/master/documentation/Data_import.md

## Running the Tests

The **Python unit tests** are just pytest tests located in the **'tests'** folder. They use
sqlite to simulate database when needed. As a result they can't cover code using
Postgres features. To run the tests manually, you may to have to point PYTHONPATH
to your Medex Git clone:

    export PYTHONPATH=$(pwd)
    pytest tests

The **Python integration tests** are als pytest tests but are located in **'integrations_tests'**
and will use docker to run a Postgres Database on port 5477. Either the old
docker-compose binary or a modern docker with the plugin for compose subcommand
must be installed.

The **TypeScript tests** are located in the same folders as the source (`*.test.mts`).
To execute them, the TypeScript compiler (tsc) must be executable. So you may
have to add `node_modules/.bin` to your path. To execute the tests run:

    npm run test

## Revision History

* XXX
  * Changed build system to vite, explicity compiling typia templates

* v1.0.1 - 2023-09-08:
  * Basic Stats/Database: Patient count is incorrect if case_id field is used
  * Histogram: Nicer measurement labels in some cases
  * NodeJS modules: updated - including tough-cookie (now 4.1.3)

* v1.0.0 - 2023-08-30:
  * Caching filter data per session in database to allow efficient and correct filtering
  * Migrated frontend to TypeScript with ReactJS
  * Replacing Bootstrap v4 by v5
  * Updated almost all JavaScript dependencies
  * Using schema versioning with Alembic
  * Refactoring database schema to match naming conventions in source

* v0.1.4 - 2022-08-08:
  * multiple database sessions
  * SQlalchemy integrated into the tool
  * restriction of data selection
  * ajax for data filtering

* v0.1.3 - 2021-10-14:
  * selection a time range for data 
  * filters IDs by categorical values 
  * filter IDs by numerical values 
  * possibility to connect with another web app

* v0.1.2 - 2021-06-04:
  * possibility to add visit 
  * synonyms and description for entities 
  * a table browser tab to display data from the database 
  * categorical filters for data 
  * better jQuery functionality

* v0.1.1 - 2020-04-03:
  * uniform plot visualization 
  * added categorical value to the scatter plot 
  * better error handling for unexpected actions and entries by the user

* v0.1.0 - 2020-02-12:
  * Frontend has been tested for possible bugs 
  * Error handling for unexpected actions and entries by the user 
  * Informative warnings 
  * Adjustable binsize for the histogram

## Citation

Aljoscha Kindermann, Ekaterina Stepanova, Hauke Hund, Nicolas Geis, Brandon Malone, Christoph Dieterich (2019) 
**MedEx - Data Analytics for Medical Domain Experts in Real-Time**
