import pandas as pd
import numpy as np
from collections import ChainMap

def get_categorical_entities(r):
    """ Retrieve  categorical entities and their subcategories from PostrgreSQL

    get_categorical_entities use in webserver

    r: connection with database

    Returns
    -------
    df["Key"]: list of all categorical entities

    df: dictionary with categorical entities and subcategories of categorical entities
    """

    # Retrieve all categorical values
    sql1 = """Select "Key" from name_type where "type" = 'String' order by "Key" """

    # Retrieve categorical values with subcategories
    sql2 = """Select distinct "Key","Value" from examination_categorical order by "Key","Value" """
    try:
        df1 = pd.read_sql(sql1, r)
        df = pd.read_sql(sql2, r)

        array = []

        # create dictionary with categories and subcategories
        for value in df1['Key']:
            dfr2 = {}
            df2 = df[df["Key"] == value]
            del df2['Key']
            dfr2[value] = list(df2['Value'])
            array.append(dfr2)
        df = dict(ChainMap(*array))
        return df1["Key"], df
    except Exception:
        return ["No data"], ["No data"]




def get_numeric_entities(r):
    """ Retrieve numerical entities from PostgreSQL

    get_numeric_entities use in websever

    r: connection with database

    Returns
    -------
    df["Key"]: list of all numerical entities
    """
    try:
        sql = """Select "Key" from name_type where type = 'Double' order by "Key" """
        df = pd.read_sql(sql, r)
        return df['Key']
    except Exception:
        return ["No data"]


def number(r):
    """ Get number of all patients

     number use only for basic_stats
     """
    try:
        sql = """SELECT COUNT (*) FROM Patient"""
        n = pd.read_sql(sql, r)
        return n['count'],None
    except Exception:
        return None, "Problem with load data from database"


def get_values(entity, r):
    """ Get numerical values from numerical table  from database

    get_values use in scatter plot, heatmap, clustering, coplots

    r: connection with database

    Returns
    -------
    df: DataFrame with columns Patient_ID,entity1,entity2,...

    """

    entity_fin = "'" + "','".join(entity) + "'"

    sql = """SELECT "Patient_ID","Key","Value" FROM examination_numerical WHERE "Key" IN ({})""".format(entity_fin)
    try:
        df = pd.read_sql(sql, r)
        df = df.pivot_table(index="Patient_ID", columns="Key", values="Value", aggfunc=np.mean).reset_index()
        return df, None
    except Exception:
        return None, "Problem with load data from database"



def get_cat_values(entity, subcategory, r):
    """ Get categorical values from database

    get_cat_values use in scatter plot and coplots

    r: connection with database

    Returns
    -------
    df: DataFrame with columns Patient_ID,entity

    """

    subcategory_fin = "'" + "','".join(subcategory) + "'"

    sql = """SELECT "Patient_ID","Value" FROM examination_categorical WHERE "Key"= '{0}' 
            and "Value" IN ({1})""".format(entity, subcategory_fin)
    try:
        df = pd.read_sql(sql, r)
        df.columns = ["Patient_ID", entity]
        return df, None
    except Exception:
        return None, "Problem with load data from database"


def get_cat_values_barchart(entity, subcategory, r):
    """ Get number of subcategory values from database

    get_cat_values_barchart use only for barchart

    r: connection with database

    Returns
    -------
    df: DataFrame with columns Patient_ID,Key,Value

    """
    try:
        subcategory = "'" + "','".join(subcategory) + "'"
        sql = """SELECT "Value",count("Value") FROM examination_categorical WHERE "Key"='{0}'
                and "Value" IN ({1}) group by "Value" """.format(entity, subcategory)
        df = pd.read_sql(sql, r)
        df.columns = [entity, 'count']
        return df,None
    except Exception:
        return None, "Problem with load data from database"


def get_cat_values_basic_stas(entity, r):
    """ Get number of categorical values from database

    get_cat_values_basic_stas use only for basic_stas categorical

    r: connection with database

    Returns
    -------
    df: DataFrame with columns Key,count

    """
    try:
        entity_fin = "'" + "','".join(entity) + "'"
        sql = """SELECT "Key",count("Key") FROM examination_categorical WHERE "Key" IN ({})
                group by "Key" """.format(entity_fin)
        df = pd.read_sql(sql, r)
        df = df.pivot_table(columns="Key", values="count")
        return df, None
    except Exception:
        return None, "Problem with load data from database"


def get_num_cat_values(entity_num, entity_cat, subcategory, r):
    """ Retrieve categorical and numerical value

    get_num_cat_values use in histogram and boxplot

    r: connection with database

    Returns
    -------
    df: DataFrame with columns Patient_ID,entity_num,entity_cat
     """
    try:
        subcategory = "'" + "','".join(subcategory) + "'"

        sql = """SELECT en."Patient_ID",en."Value" as "{0}",ec."Value" as "{1}" FROM examination_numerical as en 
                left join examination_categorical as ec on en."Patient_ID" = ec."Patient_ID" 
                where en."Key" = '{0}' and ec."Key" = '{1}' 
                and ec."Value" IN ({2}) order by ec."Value" """.format(entity_num, entity_cat, subcategory)

        df = pd.read_sql(sql, r)
        return df,None
    except Exception:
        return None, "Problem with load data from database"




