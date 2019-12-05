#! /usr/bin/env python3

import argparse
import collections
import datetime
import itertools
import time
import shlex

import pandas as pd
import redis
import tqdm


# helpers for the nlp stuff
import nltk.corpus
import nltk.stem.snowball
import nltk.tag.stanford

import misc.utils as utils

# connect to redis
import data_warehouse.redis_rwh as rwh

import logging
import misc.logging_utils as logging_utils
logger = logging.getLogger(__name__)

# default_host = "129.206.148.189"
default_host = "127.0.0.1"
default_port = 6379
default_entities_to_keep = []


# example of the command:  python load_redis.py dataset_examples/sample_diagnostic_data.csv dataset_examples/entities.csv --host 127.0.0.1 --port 6379
def update_db(
        line, 
        r, 
        entities, 
        number_keys, 
        category_keys, 
        category_values, 
        date_keys, 
        stopwords, 
        stemmer,
        entities_to_keep
    ):

    lexer = shlex.shlex(line.strip(), posix=True)
    lexer.whitespace_split = True
    lexer.whitespace = ","
    (patient_id, quarter_id, date_stamp, time_stamp, key, value) = lexer

    if entities_to_keep is not None:
        if key not in entities_to_keep:
            return None

    #patient_id = patient_id.decode()
    #quarter_id = quarter_id.decode()
    #key = key.decode()
    #value = value.decode()

    
    # first, just check if the value is a number
    float_value = utils.try_parse_float(value)
    entity_type = entities.get(key)
    
    s = None
    if float_value is not None:
        r.zadd(key, float_value, patient_id)
        s = ("ZADD {} {} {}".format(key, float_value, patient_id))
        
        number_keys.add(key)

    elif entity_type == 'String':
        value = [stemmer.stem(word) for word in value if word not in stopwords]
        value = ' '.join(value)


        kv = "{}.{}".format(key, value)
        r.sadd(kv, patient_id)
        s = ("SADD {} {}".format(kv, patient_id))

        category_keys.add(key)
        category_values[key].add(value)
        
    elif entity_type in ['Integer', 'Double']:
        # i don't think we will ever be here
        float_value = utils.try_parse_float(value)
        r.zadd(key, float_value, patient_id)
        s = ("ZADD {} {} {}".format(key, float_value, patient_id))

        number_keys.add(key)

    elif entity_type == 'null':
        value = time.mktime(datetime.datetime.strptime(date_stamp, "%Y-%m-%d").timetuple())
        
        value = max(value, 0)
        r.zadd(key, value, patient_id)
        s = ("ZADD {} {} {}".format(key, value, patient_id))

        date_keys.add(key)
        
    return s

def main():
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description="This script parses the rwh_export file and load the values "
        "into the specified redis database.")

    parser.add_argument('entities', help="The pldm.entities file")
    parser.add_argument('data', help="The rwh_export file")

    parser.add_argument('-n', '--num-entries', help="If this number is given, "
        "then only this many entries will be loaded to the database.", type=int,
        default=None)

    parser.add_argument('-f', '--flush', help="If this flag is given, then "
        "the existing entries will be flushed from the database", 
        action='store_true')

    parser.add_argument('--host', help="The hostname of the redis database",
        default=default_host)

    parser.add_argument('-p', '--port', help="The port on which the database "
        "engine is listening", default=default_port)

    parser.add_argument('--entities-to-keep', help="If this list is given, "
        "then only these entities will be added to the database", nargs='*',
        default=default_entities_to_keep)

    
    logging_utils.add_logging_options(parser)
    args = parser.parse_args()
    logging_utils.update_logging(args)

    msg = "Reading the entities information"
    logger.info(msg)

    entities_df = pd.read_csv(args.entities, names=['name', 'value_type'])
    entities_map = utils.dataframe_to_dict(entities_df, 'name', 'value_type')

    msg = "Opening connection to redis database, host:port {}:{}".format(args.host, args.port)
    logger.info(msg)

    r = rwh.get_connection(host=args.host, port=args.port)

    if args.flush:
        msg = "Flushing the database"
        logger.info(msg)
        r.flushall()

    msg = "Extracting stop words from nltk german list"
    logger.info(msg)

    nltk.download('stopwords')
    stopwords = {
        w for w in nltk.corpus.stopwords.words('german')
    }

    msg = "Creating stemmer"
    logger.info(msg)
    stemmer = nltk.stem.SnowballStemmer('german')

    msg = "Adding entries to the database"
    logger.info(msg)

    if args.num_entries is None:
        msg = "Counting the number of entries in the file"
        logger.info(msg)

        args.num_entries = utils.count_lines(args.data)

        msg = "Found {} entries".format(args.num_entries)
        logger.info(msg)

    num_problems = 0
    problem_lines = []

    number_keys = set()
    category_keys = set()
    category_values = collections.defaultdict(set)
    date_keys = set()

    entities_to_keep = None
    if len(args.entities_to_keep) > 0:
        entities_to_keep = set(args.entities_to_keep)
    
    with open(args.data) as f:
        f = itertools.islice(f, args.num_entries)
        for line in tqdm.tqdm(f, total=args.num_entries):
            try:
                update_db(line, r, entities_map, number_keys, category_keys, 
                    category_values, date_keys, stopwords, stemmer, entities_to_keep)
            except Exception as e:
                msg = "Problem: {}".format(line)
                logger.debug(msg)
                logger.debug(str(e))
                #problem_lines.append(line)
                num_problems += 1

    msg = "Encountered {} problems while loading database".format(num_problems)
    logger.warning(msg)

    msg = "Adding the list of numeric entities"
    logger.info(msg)

    for number_key in number_keys:
        r.sadd("number_keys", number_key)

    msg = "Adding the list of date entities"
    logger.info(msg)

    for date_key in date_keys:
        r.sadd("date_keys", date_key)

    msg = "Adding the list of categorical entities"
    logger.info(msg)

    for category_key in category_keys:
        r.sadd("category_keys", category_key)

    msg = "Adding the list of values for each categorical entitiy"
    logger.info(msg)

    for category, cv in category_values.items():
        category_key = "{}_values".format(category)
        for category_value in cv:
            r.sadd(category_key, category_value)

    # no need to "close" the redis connection. 
    # See: http://stackoverflow.com/questions/24875806

if __name__ == '__main__':
    main()
