import click
import pandas as pd

import data_warehouse.redis_rwh as rwh

"""
Use to import data of the rwh style format into redis. 
RWH format: Patient_ID,Billing_ID,Date,Time,Key,Value
Example file starts like this:
f96ae85e2c3598e7eefa593a927fe1c8,d41d8cd98f00b204e9800998ecf8427e,2012-07-13,4:51:9,Gender,male
f96ae85e2c3598e7eefa593a927fe1c8,d41d8cd98f00b204e9800998ecf8427e,1999-03-13,15:26:20,Jitter_rel,0.25546
...    

Also necessary is an "entities file" specifying the data type, which can be String or Double. 
In our Example that would be a file starting like this:
entity,datatype
Gender,String
Jitter_rel,Double
...

Usage of the loading script: 
python import_dataset.py <input_data_file> <input_entities_file>
"""


def import_entity_types(entity_file):
    entities = pd.read_csv(entity_file)
    # Name is first, Type is second column
    numeric_entities = set(entities[(entities["datatype"] == "Double") | (entities["datatype"] == "Integer")]["entity"])
    categorical_entities = set(entities[entities["datatype"] == "String"]["entity"])
    print("Numeric keys: ", numeric_entities)
    print("Categoric keys: ", categorical_entities)
    return numeric_entities, categorical_entities


def clear_database(rdb):
    rdb.flushall()


def import_dataset(url, input_file, numeric_entities, categorical_entities):
    num_imp, cat_imp, num_err, not_imp = [0, 0, 0, 0]
    numeric_value_errors = { }
    categorical_values = { }
    rdb = rwh.get_connection(url=url)
    clear_database(rdb)
    print("Starting putting data into redis")
    # run again to have the categories and numerics now ready and write the data
    with open(input_file) as infile:
        # loop over input file, getting the data type at the same time
        for n, line in enumerate(infile):
            # we assume that the file is always Patient_ID, Billing_ID, Date, Time, Key, Value
            linelist = line.replace("\n", "").split(",")
            # last column 6 might be having commas
            Patient_ID, Billing_ID, rwh_Date, rwh_Time, rwh_Key, rwh_Value = linelist[0:5] + [
                ",".join([str(x) for x in linelist[5:]])]



            # Test if Value is numeric or string
            if rwh_Key in categorical_entities:
                rdb.sadd('{}.{}'.format(rwh_Key, rwh_Value), Patient_ID)
                cat_imp += 1
                if rwh_Key in numeric_entities:
                    numeric_entities.remove(rwh_Key)
                # Add value to the dictionary of possible values (setdefault avoids duplicates)
                categorical_values.setdefault(rwh_Key, [])
                categorical_values[rwh_Key].append(rwh_Value)
            elif rwh_Key in numeric_entities:
                try:
                    value = float(rwh_Value)
                    rdb.zadd(rwh_Key, { Patient_ID: rwh_Value })
                    num_imp += 1
                except ValueError:
                    numeric_value_errors.setdefault(rwh_Key, set())
                    numeric_value_errors[rwh_Key].add(rwh_Value)
                    num_err += 1
            else:
                not_imp += 1
                pass
                # we assume that we can add everything that was not cleaned (not in entity file) as string, but mark it "unclean"
                # print(rwh_Value, "was not added, no entity type defined. Line: ", line)
                ##rwh_Key = "uncleaned_" + rwh_Key
                ##rdb.sadd('{}.{}'.format(rwh_Key, rwh_Value), Patient_ID)
                # Add value to the dictionary of possible values (setdefault avoids duplicates)
                ##categorical_values.setdefault(rwh_Key, [])
                ##categorical_values[rwh_Key].append(rwh_Value)

    # Add the specified members to the set stored at key.
    for entity in numeric_entities:
        rdb.sadd("number_keys", entity)

    for entity in categorical_entities:
        rdb.sadd("category_keys", entity)

    for category, values in categorical_values.items():
        entity = "{}_values".format(category)
        for value in values:
            rdb.sadd(entity, value)
    print("The following numerics were not valid and therefore not added:\n", numeric_value_errors)
    print("\nNumeric values imported: %i\nCategorical values imported: %i\nErrors in numeric values: %i\nOther errors: %i\n" % (
        num_imp, cat_imp, num_err, not_imp))


