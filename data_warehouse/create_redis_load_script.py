#! /usr/bin/env python3

import argparse
import csv
import datetime
import time
import pandas as pd

import tqdm

import logging
import misc.logging_utils as logging_utils
logger = logging.getLogger(__name__)

def print_db_statement(line, entities, out):
    (patient_id, quarter_id, date_stamp, time_stamp, key, value) = line # line.strip().split(",")
    entity_type = entities.get(key)
    if entity_type is None:
        return None

    if entity_type == 'String':
        kv = "{}.{}".format(key, value)
        #r.sadd(kv, patient_id)
        out.write("SADD {} {}\n".format(kv, patient_id))
    elif entity_type in ['Integer', 'Double']:
        #r.zadd(key, value=patient_id)
        out.write("ZADD {} {} {}\n".format(key, value, patient_id))
    elif entity_type == 'null':
        value = time.mktime(datetime.datetime.strptime(date_stamp, "%Y-%m-%d").timetuple())
        
        value = max(value, 0)
        #r.zadd(key, patient_id=value)
        out.write("ZADD {} {} {}\n".format(key, value, patient_id))

def main():
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description="")

    parser.add_argument('entities')
    parser.add_argument('data')
    parser.add_argument('out')
    
    logging_utils.add_logging_options(parser)
    args = parser.parse_args()
    logging_utils.update_logging(args)
    entities_df = pd.read_csv(args.entities, names=['name', 'value_type'])

    entities = {
        row['name']: row['value_type']
            for (index, row) in entities_df.iterrows()
    }
    # total = 64946577 # is it the number of lines?
    # if total is defined as (len(list(csv_data)), then for some reason data_iter becomes empty.
    with open(args.data) as data, open(args.out, 'w') as out:
        csv_data = csv.reader(data)
        data_iter = tqdm.tqdm(csv_data)#, total=total)
        for line in data_iter:
            try:
                print_db_statement(line, entities, out)
            except:
                msg = "Problem: {}".format(line)
                logger.warning(msg)

if __name__ == '__main__':
    main()
