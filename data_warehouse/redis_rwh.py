###
#   This module contains high-level functions for querying the redis database
#   for the RWH project.
###
import collections

import numpy as np
import pandas as pd

def get_connection(host="localhost", port=6379, url=None):
    """ Get a connection to the redis database server. 
    
    After opening the connection, a test ping is sent to ensure the connection
    is valid.

    host: string
        The host name. "129.206.148.189" is the redis vm on the cluster

    port: int
        The connection port. 6379 is the default port for redis

    Returns
    -------
    connection: redis.StrictRedis
        The connection to the server

    Raises
    ------
    ConnectionError
        If the ping fails
    """
    import redis
    if url:
        print(url)
        r = redis.StrictRedis.from_url(url=url)
    else:
        r = redis.StrictRedis(host=host, port=port)

    r.ping()
    return r


def _get_sorted_values(key, r):
    """ Retrieve all values associated with the given key as a sorted list

    Parameters
    ----------
    key : string
        The key whose values to find

    r : redis.StrictRedis
        The redis database connection

    Returns
    -------
    sorted_values : np.array of strings
        All values associated with the key, sorted
    """
    res = r.smembers(key)
    res_np = np.array(list(res), dtype=str)
    res_np = np.sort(res_np)
    return res_np


def get_categorical_entities(r):
    """ Retrieve the names of all categorical entities in the database

    Parameters
    ----------
    r : redis.StrictRedis
        The redis database connection

    Returns
    -------
    categorical_entities : np.array of strings
        The (sorted) names of all the categorical entities
    """
    categorical_entities = _get_sorted_values("category_keys", r)
    return categorical_entities


def get_date_entities(r):
    """ Retrieve the names of all date entities in the database

    Parameters
    ----------
    r : redis.StrictRedis
        The redis database connection

    Returns
    -------
    date_entities : np.array of strings
        The (sorted) names of all the date entities
    """
    date_entities = _get_sorted_values("date_keys", r)
    return date_entities


def get_numeric_entities(r):
    """ Retrieve the names of all numeric entities in the database

    Parameters
    ----------
    r : redis.StrictRedis
        The redis database connection

    Returns
    -------
    numeric_entities : np.array of strings
        The (sorted) names of all the numeric entities
    """
    numeric_entities = _get_sorted_values("number_keys", r)
    return numeric_entities


def get_category_values(entity, r):
    """ Find all of the values for the given categorical entity

    Parameters
    ----------
    entity : string
        The name of the categorical entity

    r : redis.StrictRedis
        The redis database connection

    Returns
    -------
    entity_values : set of strings
        All values for the given entity in the database. If the entity is not
        present in the database (or is numeric), then the set will be empty.
    """
    key = "{}_values".format(entity)
    entity_values = r.smembers(key)
    entity_values = { v.decode() for v in entity_values }
    return entity_values


def get_categorical_value_set(categorical_entity, value):
    """ Get the name of the set for patients with the given value for the 
    categorical entity.

    """
    return "{}.{}".format(categorical_entity, value)


def get_entity_mean_var(entity, r):
    """ Find the mean and variance of a numeric entity

    Parameters
    ----------
    entity : string
        The name of the numeric entity

    r : redis.StrictRedis
        The redis database connection

    Returns
    -------
    mean, variance : floats
        The mean and variance of the values for the entity
    """
    from misc.incremental_gaussian_estimator import IncrementalGaussianEstimator

    ige = IncrementalGaussianEstimator()
    it = r.zscan_iter(entity)

    for (patient_id, val) in it:
        ige.add_observation(val)

    return ige.get_mean(), ige.get_var()


def get_entity_values(field, r):
    """ Retrieve all of the unique values (scores) of a numeric entity

    Parameters
    ----------
    entity : string
        The name of the numeric entity

    r : redis.StrictRedis
        The redis database connection

    Returns
    -------
    entity_values : np.array of objects
        A numpy array containing all of the values for the entity
    """
    vals = []
    it = r.zscan_iter(field)

    for (patient_id, val) in it:
        vals.append(val)

    return np.array(vals)


def get_patients_with_category_value(entity, value, r):
    """ Retrieve all patients which have the specified value for a categorical
    entity.

    N.B. A patient can have more than one value for a particular entity. For
    example, "diagnostik.nebendiagnose.icd.kode" is an entity, and a patient
    can have multiple values (i.e., associated ICD codes).

    Parameters
    ----------
    entity : string
        The name of the categorical entity

    value : string
        The value for the entity

    r : redis.StrictRedis
        The redis database connection

    Returns
    -------
    patient_ids : set of strings
        All patient IDs which have the entity and value

    """
    key = "{}.{}".format(entity, value)
    res = r.smembers(key)
    res = { r.decode() for r in res }
    return res


def get_joined_numeric_values(entities, r, min_max_filter=None):
    """ Retrieve the values of the given numeric entities for all patients

    Parameters
    ----------
    entities : list-like of strings
        The numeric entities whose values will be retrieved

    r : redis.StrictRedis
        The redis database connection

    Returns
    -------
    merged_df : pd.DataFrame
        A data frame containing the values of the selected entities for all patients
        which have at least one of the entities. Patients which do not have
        values of any of the entities are not included in the output. Missing
        values are represented with "NaN"s.

        The data frame contains one column for each entity, plus an additional
        column containing the patient id.

        The "dropna" method of the data frame could be used to remove patients
        which do not have values for all entities.
    """

    merged_df = None
    for entity in entities:
        min_value, max_value = min_max_filter[entity] if min_max_filter and entity in min_max_filter else ('-inf', '+inf')
        values = r.zrangebyscore(entity, min_value, max_value, withscores=True)
        df = pd.DataFrame(values)
        if len(df) == 0:
            # stop the join if atleast one entity has no values
            return None, entity + " has no values"
        df.columns = ['patient_id', entity]
        merged_df = df.copy() if merged_df is None else pd.merge(merged_df, df, how='outer', on='patient_id')

    merged_df['patient_id'] = merged_df['patient_id'].apply(lambda x: x.decode())
    return merged_df, None


def get_all_patients_category_value(entity, r):
    """ Find the value for a categorical entity for all patients.
    
    Parameters
    ----------
    entity : string
        The name of the categorical entity

    r : redis.StrictRedis
        The redis database connection
        
    Returns
    -------
    patient_values_df : pd.DataFrame
        A data frame which contains the value of the given entity
        for all patients which have a value for it in the database
    """

    all_dfs = []

    # first, we need to get all of the values for this category
    category_values = rwh.get_category_values(entity, r)

    # now, find all the patients with each value
    for category_value in category_values:
        patient_ids = rwh.get_patients_with_category_value(entity, category_value, r)

        df = pd.DataFrame()
        df['patient_id'] = list(patient_ids)
        df[entity] = category_value

        all_dfs.append(df)

    all_df = pd.concat(all_dfs)
    return all_df


def get_joined_categorical_values(entities, r):
    """ Retrieve the values of the given categorical entities for all patients
    
    
    Parameters
    ----------
    entities : list-like of strings
        The categorical entities whose values will be retrieved

    r : redis.StrictRedis
        The redis database connection

    Returns
    -------
    values_df : pd.DataFrame
        A data frame containing the values of the entities for all patients
        which have at least one of the entities. Patients which do not have
        values of any of the entities are not included in the output. Missing
        values are represented with "NaN"s.

        The data frame contains one column for each entity, plus an additional
        column containing the patient id.

        The "dropna" method of the data frame could be used to remove patients
        which do not have values for all entities.
    """
    values_dict = { }
    for entity in entities:
        # first, we need to get all of the values for this category
        category_values = get_category_values(entity, r)
        if len(category_values) == 0:
            return None, entity + " has no values"
        # now, find all the patients with each value
        for category_value in category_values:
            # for some reason the value has spaces between charachters
            key = get_categorical_value_set(entity, category_value)
            it = r.sscan_iter(key)
            for patient_id in it:
                if patient_id not in values_dict:
                    values_dict[patient_id] = { }
                if entity not in values_dict[patient_id]:
                    values_dict[patient_id][entity] = category_value.replace(' ', '')
    rows = []
    for patient_id in values_dict.keys():
        row = collections.OrderedDict()
        row['patient_id'] = patient_id
        for entity in values_dict[patient_id].keys():
            row[entity] = values_dict[patient_id][entity]
        rows.append(row)

    values_df = pd.DataFrame(rows)
    # values_df['patient_id'] = values_df['patient_id'].apply(lambda x: x.decode())
    # return values_df
    values_df['patient_id'] = values_df['patient_id'].apply(lambda x: x.decode())
    return values_df, None


def get_patient_info(
        patient_id,
        r,
        all_numeric_entities=None,
        all_categorical_entities=None,
        all_date_entities=None):
    """ Extract all information from all entities about the given patient.

    Optionally, a set of entities can be passed, and only those will be 
    included in the results.

    Parameters
    ----------
    patient_id: string
        The anonymized patient id

    r: redis.StrictRedis
        The redis database connection

    all_{numeric, categorical, date}_entities: list-likes
        If provided, then only these entities will be included in the results.
        To skip an entity type, an empty list (*not* None) can be given.

    Returns
    -------
    patient_info: dict
        A mapping from each entity to the value for this patient. Missing
        entities are not included in the results.
    """

    if all_numeric_entities is None:
        all_numeric_entities = rwh.get_numeric_entities(r)

    if all_categorical_entities is None:
        all_categorical_entities = rwh.get_categorical_entities(r)

    if all_date_entities is None:
        all_date_entities = rwh.get_date_entities(r)

    patient_info = { "patient_id": patient_id }

    for numeric_entity in all_numeric_entities:
        score = r.zscore(numeric_entity, patient_id)
        if score is not None:
            patient_info[numeric_entity] = score

    for categorical_entity in all_categorical_entities:
        category_values = get_category_values(categorical_entity, r)

        for category_value in category_values:
            key = get_categorical_value_set(categorical_entity, category_value)

            if r.sismember(key, patient_id):
                patient_info[categorical_entity] = category_value

    return patient_info


def get_all_patient_info(patient_ids, r):
    """ Extract all information about all of the given patients.

    This is mostly a wrapper around get_patient_info, so please see the
    documentation for that function for more information.

    Parameters
    ----------
    patient_ids: list-like
        The patient identifiers
    
    r: redis.StrictRedis
        The redis database connection

    Returns
    -------
    patient_info_df: pandas.DataFrame
        A data frame containing the values for each patient. Missing values
        are represented with NaNs (*not* Nones).

    """
    all_numeric_entities = get_numeric_entities(r)
    all_categorical_entities = get_categorical_entities(r)
    all_date_entities = get_date_entities(r)

    all_patient_info = [
        get_patient_info(
                patient_id,
                r,
                all_numeric_entities=all_numeric_entities,
                all_categorical_entities=all_categorical_entities,
                all_date_entities=all_date_entities
                ) for patient_id in patient_ids
        ]

    return pd.DataFrame(all_patient_info)
