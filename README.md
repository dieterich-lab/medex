# MedEx - Medical Data Explorer

This project provides a dashboard tool to allow a quick exploratory data analysis of datasets.
It was developed to allow a quick insight into our medical research-data-warehouse without the need of knowing how to use SQL or programming languages. 
However, it is not limited to clinical data, but can be used to do exploratory data analysis on many kind of datasets. 

## Production Setup

### Requirements

* Linux/MacOs
* [Docker-CE](https://docs.docker.com/install/) >= 18.09.07

### Usage

1. Make sure that Docker Swarm is enabled. In doubt do:

       sudo docker swarm init

2. Go to your medex copy.

3. Build the medex image:

        docker build .

4. Tag the image:

        docker tag <ID from above command> medex:latest

5. Create your stack-compose.yml based on the example in the folder ./examples.

6. Run a docker stack with that:

        docker stack deploy medex --compose-file the configuration file.-compose.yml

Setups with 'docker-compose', or the 'docker compose' sub command in newer
Docker versions are known to work too, but may require minor changes to
the configuration file.

Test it out at http://localhost:8000. No mounted folders. To apply changes, the image must be re-built. <br>

## Development Setup

### Requirements

* Linux/MacOS
* [Python](https://www.python.org/) >= 3.8
* [Docker-CE](https://docs.docker.com/install/) >= 18.09.07

### Usage

1. Create a Python venv with your preferred method and activate it:
   * E.g. using your IDE's mechanism (PyCharm)
   * or manually:

         python3 -m venv /where/ever/my/venv
         . /where/ever/my/venv

2. Install pipenv in this venv:

       pip install pipenv

3. Go to your mdex working copy

4. Install both the run-time and the development dependencies:

       pipenv install
       pipenv install --dev

5. Bring up a database. You may use the configuration under ./examples for that:

       ( cd examples/docker_database_only && docker-compose up -d )

6. Bring up application itself:

       ./scripts/start.sh
   

Test it out at http://localhost:5000. The "web" folder is mounted into the container and your code changes apply automatically.

**Hint for PyCharm users:** To use the PyCharm's debugger easily you may prefer
to create "Run Configuration" in PyCharm instead of using 'start.sh'. To do that,
you need to copy the environment variables from that script to the run configuration.

## Data Import

Data is imported from the 'import' directory during the start of the application,
when it seems necessary (e.g. first run or after change of the input files).

For details see: https://github.com/dieterich-lab/medex/tree/master/dataset_examples/Data_import.md

## Running the Tests

The **unit tests** are just pytest tests located in the **'tests'** folder. They use
sqlite to simulate database when needed. That limits their ability to test code,
which uses Postgres features.

The **integration tests** are als pytest tests but are located in **'integrations_tests'**
and will use docker to run a Postgres Database on port 5477. Either the old
docker-compose binary or a modern docker with the plugin for compose subcommand
must be installed.

## Citation

Aljoscha Kindermann, Ekaterina Stepanova, Hauke Hund, Nicolas Geis, Brandon Malone, Christoph Dieterich (2019) 
**MedEx - Data Analytics for Medical Domain Experts in Real-Time**
