Research Data Warehouse
=======================

Install app
-----------

1. Set up a virtual environment (e.g. conda). Use python version 3.x:

``
conda create -n rd_warehouse python=3
``

2. Get source code from gihub:

``git clone https://github.com/dieterich-lab/data-warehouse.git``

3. Install using pip:

``pip install --verbose -e .``

4. Set up environment.
Export environmental variables `FLASK_APP`:
``cd flaskr && export FLASK_APP=hello.py`` (note that on Ubuntu, it has to be done from the `flaskr` directory)
and `FLASK_ENV`:
``export FLASK_ENV=development``

5. Install redis:
Installation instructions can be found here: https://redis.io/topics/quickstart
Otherwise:

``
wget http://download.redis.io/redis-stable.tar.gz
tar xvzf redis-stable.tar.gz
cd redis-stable
make
``
6. Run redis.
The following command will run redis on localhost, port 6379
``redis-server``

7. Run app:
The following command will run datawarehouse app on localhost, port 5000.
This has to be run from the `datawarehouse/flaskr` directory.
``flask run``

Import errors
-------------
In case of import errors, just install missing packages with the command `pip install XXX` and add the package to `setup.py`.


Dataset import
--------------
The dataset can be imported from a csv file
There are 2 ways for that:

1. via `load_redis.py` script

There are 2 csv files required to import the data to redis. One should contain the data itself, and each line should look something like that:

00764cd6bc5ba87940871af9d8690321,33ee13c1963da2156c21fb7d890014d1,2018-05-30,11:37:00,diagnostik.labor.clump_thickness,4
where the columns are patient_id, quarter_id, date_stamp, time_stamp, entity_name, entity_value (respectively)

The second one should contain the unique set of the entities from the main csv file (column 5 (starting from 1)) and their types.
For example: `diagnostik.labor.clump_thickness,String`

This file can be generated from the main .csv file

Examples of both files are in the directory dataset_examples (sample_diagnostic_data.csv and entities.csv)

Example of the command:

``
python load_redis.py dataset_examples/sample_diagnostic_data.csv dataset_examples/entities.csv --host 127.0.0.1 --port 6379
``

2. via `create_redis_load_script.py`

This script does not import the data directly in redis, but it creates an output file with the list of commands which can be further given to redis.

It requires again the 2 csv files, one containing the data, and another one containing the relations between entities and their types.

The script also requires a path to the output file, where the commands will be written.

Example:

``
python create_redis_load_script.py dataset_examples/entities.csv dataset_examples/sample_diagnostic_data.csv dataset_examples/create_redis_load_script_output.txt
``

If the output file does not exist, it will be created. Example of the output:

``ZADD diagnostik.labor.single_epithelial_cell_size 3 00764cd6bc5ba87940871af9d8690321
SADD diagnostik.labor.bland_chromatin.2 00764cd6bc5ba87940871af9d8690321``

The example of the `create_redis_load_script_output.txt` file can also be found in the dataset_examples directory

Then to insert the data in redis, use the following command:

``cat create_redis_load_script_output.txt | redis-cli --pipe``