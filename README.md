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

### Setup Instructions Development ###
Not recommended for pure deployment.

#### Requirements ####
* [Python](https://www.python.org/) >= 3.7
* [pipenv](https://docs.pipenv.org/en/latest/) >= 2018.10.13
* Linux/MacOS

#### Usage ####
* `pipenv install` installs the latest dependencies
* `pipenv shell` enters the virtual environment
* `docker-compose up` Database exist in docker container
* `./scripts/start.sh`
* Develop

## Data Import ##
* Database imports run every night at 5:05 and at startup.
* The database is only updated if there is new data to import.

### Importing new data ###
In order to add new data add a new `header.csv`,`entities.csv` and `dataset.csv` to the `./import` folder

To work the files should have the same format as the current example files that are already in that directory. 

The file `header.csv` is used to create a table for data from the file` dataset.csv`, so it should contain the name of the column and type:

`"ID" numeric PRIMARY KEY,"Patient_ID" text,"Billing_ID" text, "Date" timestamp,"Time" text,"Key" text,"Value" text`

`header.csv` can also looks like this:

`"ID" numeric PRIMARY KEY,"Patient_ID" text,"Key" text,"Value" text`

Important at this moment is that we always need column with name "ID","Patient_ID","Key" and "Value" columns,"Billing_ID","Date" and "Time"  are not necessary. 
Name of column in file `header.csv` have to be in quotation marks.

The currently used format of the `dataset.csv` file comes from the research warehouse export format(with added ID to create Primary Key in database) of the data we are analysing with this tool :
 
`Patient_ID,Billing_ID,Date,Time,Key,Value`

Example file starts like this:
```
f96ae85e2c3598e7eefa593a927fe1c8,d41d8cd98f00b204e9800998ecf8427e,2012-07-13,4:51:9,Gender,male
f96ae85e2c3598e7eefa593a927fe1c8,d41d8cd98f00b204e9800998ecf8427e,1999-03-13,15:26:20,Jitter_rel,0.25546
```
Billing_ID, Date and Time are currently not used and are optional, required are only a unique identifier of the data instance (Patient), a parameter name and the respective value, and the six columns format, so this line works as well:
```
Patient1,,,,A_numeric_parameter,5.8
```
  
Also necessary is the entities.csv file, specifying the data type, which can be String or Double. 
In our Example that would be a file starting like this:
```
entity,datatype
Gender,String
Jitter_rel,Double
```

Example files can be found in `./dataset_examples`. To test them copy them to `./import` and restart the tool.


### Controlling the Data Import Scheduler ###
To learn more about the scheduler and the configuration methods read [here](https://apscheduler.readthedocs.io/en/latest/modules/triggers/cron.html#module-apscheduler.triggers.cron). 
The scheduler can be controlled by 4 envrionment variables:
* `IMPORT_DISABLED` disables the scheduler if any value is set
* `IMPORT_DAY_OF_WEEK` decides which days the import is run
* `IMPORT_HOUR` decides which hour it is run at i.e. 5 is 5 a.m.
* `IMPORT_MINUTE` changes the minute the import is run



## Deploy Debian Based ##
Please keep in mind that the application uses port 800 by default, that can be changed in the `./docker-compose.yml`!
This is important because it manages the application startup automatically. i.e. Autostart and Restart on Crash

1. Open service `./scripts/data-warehouse.service`
2. Change `WorkingDirectory` to current main directory
3. Copy to systemd folder; for instance, `/etc/systemd/system/`
4. Run `sudo systemctl daemon-reload`
5. Run `sudo systemctl enable data-warehouse.service`
6. Run `sudo systemctl start data-warehouse.service`
7. Check whether it runs properly



