## Data Import ##
* Database imports run every night at 5:05 and at startup.
* The database is only updated if there is new data to import.

### Importing new data ###
In order to add new data add a new `entities.csv` and `dataset.csv` to the `./import` folder

To work the files should have the same format as the current example files that are already in that directory. 

The currently used format of the dataset.csv file comes from the research warehouse export format of the data we are analysing with this tool:
 
`Patient_ID,Visit,Date,Time,Entity,Value`

Example file starts like this:
```
f96ae85e2c3598e7eefa593a927fe1c8,1,2012-07-13,4:51:9,Gender,male
f96ae85e2c3598e7eefa593a927fe1c8,0,1999-03-13,15:26:20,Jitter_rel,0.25546
```
Date and Time are currently not used and are optional, required are a unique identifier of the data instance (Patient), number of visit a parameter name and the respective value, and the six columns format, so this line works as well:
```
Patient1,,,,A_numeric_parameter,5.8
```
  
Also necessary is the entities.csv file, specifying the data type, which can be String or Double. 
In our Example that would be a file starting like this:
```
Gender,String
Jitter_rel,Double
```
If your data have entities with a different data type (ex.date), you can complete the columns with this data type, but the entity will not be taken into account in the subsequent analysis.

It is also possible to add two more columns(description,show ) to the entities.csv file.
```
Gender,String,Gender,+
Jitter_rel,Double,relative jitter,+
```

The Description column should contain a description of the entity.The description is displayed as a tooltip after hovering the cursor over the selected entity.

The show column can be empty or contain a "+" next to the entities you want to show in the "Table browser" after the program is started.

Example files can be found in `./dataset_examples`. To test them copy them to `./import` and restart the tool.


### Controlling the Data Import Scheduler ###
To learn more about the scheduler and the configuration methods read [here](https://apscheduler.readthedocs.io/en/latest/modules/triggers/cron.html#module-apscheduler.triggers.cron). 
The scheduler can be controlled by 4 environment variables:
* `IMPORT_DISABLED` disables the scheduler if any value is set
* `IMPORT_DAY_OF_WEEK` decides which days the import is run
* `IMPORT_HOUR` decides which hour it is run at i.e. 5 is 5 a.m.
* `IMPORT_MINUTE` changes the minute the import is run.

The `modules\import_scheduler` file is responsible for checking that our data was change and
 if data changed this file execute functions from import_dataset_postgre.py to create new tables with new data.
 
### Create table in database ###

Database is creating automatically during creating container for database. Environment variables of database:
* POSTGRES_USER=test
* POSTGRES_PASSWORD=test
* POSTGRES_DB=example

You can change them in docker-compose.yml

During load the data if exists tables in database they are deleted and new tables are created in their place.
Update table and adding data to table by Medex application is impossible . This option only exists if you log into the database directly [(instruction to log into database )](https://github.com/dieterich-lab/medex/blob/PostgreSQL/documentation/log_into_database.md) 
and directly execute queries in PostgreSQL database not by Medex application.


### Working on data ###

File `modules\load_data_postgre.py` contain function which contain queries necessary to load data from PostgreSQL database
to our application to allow visualization.

The functions return Python Dataframe ready to take data to visualization.

The functions are called in url_handelers files to get data for visualization.

