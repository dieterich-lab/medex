# MedEx - Medical Data Explorer
This project provides a dashboard tool to allow a quick exploratory data analysis of datasets.
It was developed to allow a quick insight into our medical research-data-warehouse without the need of knowing how to use SQL or programming languages. 
However, it is not limited to clinical data, but can be used to do exploratory data analysis on many kind of datasets. 

## Setup production ###

#### Requirements ####
* [Docker-CE](https://docs.docker.com/install/) >= 18.09.07
* [docker-compose](https://docs.docker.com/compose/overview/) >= 1.24.0

#### Usage ####
1.Open Terminal (in Windows: Command window(cmd))

2.Go to medex directory

3.Build the images and run the containers:
* `$ docker-compose up -d`

Test it out at http://localhost:8000. No mounted folders. To apply changes, the image must be re-built. <br>
[Data import information](#Data-import)

## Setup via Docker image from Docker hub ##
Instructions and a docker image are available at the link: https://hub.docker.com/r/aljoschak1/medex. <br>
It is not necessary to clone the GitHub repository.

## Setup Development [(detailed documentation)](https://github.com/dieterich-lab/medex/tree/master/documentation) ## 
Not recommended for pure deployment.

#### Requirements ####
* [Python](https://www.python.org/) >= 3.8
* [pipenv](https://docs.pipenv.org/en/latest/) >= 22.2.1
* [Docker-CE](https://docs.docker.com/install/) >= 18.09.07
* [docker-compose](https://docs.docker.com/compose/overview/) >= 1.24.0
* Linux/MacOS

#### Usage ####
1.Open Terminal 

2.Go to medex directory

3.Run commands:
* `pipenv install` installs the latest dependencies
* `pipenv shell` enters the virtual environment
* `docker-compose up` necessary for creating container for PostgreSQL database
* `./scripts/start.sh`

Test it out at http://localhost:5000. The "web" folder is mounted into the container and your code changes apply automatically.

###Data Import [(detailed documentation)](https://github.com/dieterich-lab/medex/tree/master/dataset_examples/Data_import.md)
* In order to add new data add a new `entities.csv` and `dataset.csv` to the `./import` folder.
* The `entities.csv` and `dataset.csv` files should look like in directory `dataset_examples`.
* Database imports run every night at 5:05 and at start.
* The database is only updated if there is new data to import.

## Citation ##

Aljoscha Kindermann, Ekaterina Stepanova, Hauke Hund, Nicolas Geis, Brandon Malone, Christoph Dieterich (2019) 
**MedEx - Data Analytics for Medical Domain Experts in Real-Time**