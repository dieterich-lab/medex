# MedEx - Medical Data Explorer
This project provides a dashboard tool to allow a quick exploratory data analysis of datasets.
It was developed to allow a quick insight into our medical research-data-warehouse without the need of knowing how to use SQL or programming languages. 
However, it is not limited to clinical data, but can be used to do exploratory data analysis on many kind of datasets. 

## Setup ##
We highly recommend the setup via docker-compose. The installation via pip is only recommended for developers.

### Docker Setup Instructions ###
Currently setup for deployment and not development

#### Requirements ####
* [Docker-CE](https://docs.docker.com/install/) >= 18.09.07
* [docker-compose](https://docs.docker.com/compose/overview/) >= 1.24.0

#### Usage ####
* `docker-compose up`

### Setup Instructions Development [(detailed documentation)](https://github.com/dieterich-lab/medex/tree/PostgreSQL/documentation) ### 
Not recommended for pure deployment.

#### Requirements ####
* [Python](https://www.python.org/) >= 3.7
* [pipenv](https://docs.pipenv.org/en/latest/) >= 2018.10.13
* [Docker-CE](https://docs.docker.com/install/) >= 18.09.07
* [docker-compose](https://docs.docker.com/compose/overview/) >= 1.24.0
* Linux/MacOS

#### Usage ####
* `pipenv install` installs the latest dependencies
* `pipenv shell` enters the virtual environment
* `docker-compose up` necessary for creating container for PostgreSQL database
* `./scripts/start.sh`
* Develop


### Data Import   [(detailed documentation)](https://github.com/dieterich-lab/medex/tree/time-series/dataset_examples/Data_import.md)
* Database imports run every night at 5:05 and at startup.
* The database is only updated if there is new data to import.
* In order to add new data add a new `entities.csv` and `dataset.csv` to the `./import` folder.
* The `entities.csv` and `dataset.csv` files should look like in directory `dataset_examples`.

## Citation ##

Aljoscha Kindermann, Ekaterina Stepanova, Hauke Hund, Nicolas Geis, Brandon Malone, Christoph Dieterich (2019) 
**MedEx - Data Analytics for Medical Domain Experts in Real-Time**