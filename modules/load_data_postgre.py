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

def get_visit(r):
    """ Retrieve numerical entities from PostgreSQL

    get_numeric_entities use in websever

    r: connection with database

    Returns
    -------
    df["Key"]: list of all numerical entities
    """
    try:
        sql = """Select distinct "Billing_ID" from examination order by "Billing_ID" """
        df = pd.read_sql(sql, r)
        return df['Billing_ID']
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

def get_values2(entity,visit, r):
    """ Get numerical values from numerical table  from database

    get_values use in basic_stats

    r: connection with database

    Returns
    -------
    df: DataFrame with columns Patient_ID,entity1,entity2,...

    """

    entity_fin = "'" + "','".join(entity) + "'"
    visit = "'" + "','".join(visit) + "'"

    sql = """SELECT "Patient_ID","Billing_ID","Key","Value" FROM examination_numerical2 WHERE "Key" IN ({0}) and "Billing_ID" IN ({1}) order by "Billing_ID" """.format(entity_fin,visit)
    try:
        df = pd.read_sql(sql, r)
    except Exception:
        return None, "Problem with load data from database"
    if df.empty:
        return df, "{} not measured during this visit".format(entity_fin)
    else:
        df = df.pivot_table(index=["Patient_ID", "Billing_ID"], columns="Key", values="Value",
                            aggfunc=np.mean).reset_index()
        return df, None

def get_cat_values_basic_stas2(entity,visit, r):
    """ Get number of categorical values from database

    get_cat_values_basic_stas use only for basic_stas categorical

    r: connection with database

    Returns
    -------
    df: DataFrame with columns Key,count

    """
    entity_fin = "'" + "','".join(entity) + "'"
    visit = "'" + "','".join(visit) + "'"

    sql = """SELECT "Billing_ID","Key",count("Key") FROM examination_categorical2 WHERE "Key" IN ({0}) and "Billing_ID" IN ({1})
            group by "Billing_ID","Key" """.format(entity_fin, visit)
    try:
        df = pd.read_sql(sql, r)
    except Exception:
        return None, "Problem with load data from database"
    if df.empty:
        return df, "{} not measured during this visit".format(entity_fin)
    else:
        df = df.pivot_table(index="Billing_ID", columns="Key", values="count")
    return df, None


def get_cat_values_barchart(entity, subcategory,visit, r):
    """ Get number of subcategory values from database

    get_cat_values_barchart use only for barchart

    r: connection with database

    Returns
    -------
    df: DataFrame with columns Patient_ID,Key,Value

    """
    subcategory = "'" + "','".join(subcategory) + "'"
    visit = "'" + "','".join(visit) + "'"
    sql = """SELECT "Value","Billing_ID",count("Value") FROM examination_categorical2 WHERE "Key"='{0}' and "Billing_ID" IN ({2})
            and "Value" IN ({1}) group by "Value","Billing_ID" """.format(entity, subcategory, visit)
    try:
        df = pd.read_sql(sql, r)
    except Exception:
        return None, "Problem with load data from database"
    if df.empty:
        return df, "{} not measured during this visit".format(entity)
    else:
        df.columns = [entity,'Billing_ID', 'count']
        return df,None


def barchart_visit(entities,visit,r):
    """ Get number of subcategory values from database

    get_cat_values_barchart use only for barchart

    r: connection with database

    Returns
    -------
    df: DataFrame with columns Patient_ID,Key,Value

    """
    visit = "'" + "','".join(visit) + "'"
    entities = "'" + "','".join(entities) + "'"

    sql = """SELECT count("Patient_ID"),"Billing_ID","Key" 
                from examination_categorical2  where "Key" IN ({}) and "Billing_ID" IN ({}) group by "Billing_ID","Key" """.format(entities,visit)
    sql2 = """SELECT count("Patient_ID"),"Billing_ID","Key" 
                    from examination_numerical2  where "Key" IN ({}) and "Billing_ID" IN ({}) group by "Billing_ID","Key" """.format(entities,visit)
    try:
        df1 = pd.read_sql(sql, r)
        df2 = pd.read_sql(sql2, r)
    except Exception:
        return None, "Problem with load data from database"
    df = pd.concat([df1, df2])
    if df.empty:
        return None, "The entity {} wasn't measured".format(entities)
    else:
        return df, None






def get_values(entity,visit, r):
    """ Get numerical values from numerical table  from database

    get_values use in scatter basic_stats,plot, heatmap, clustering, coplots

    r: connection with database

    Returns
    -------
    df: DataFrame with columns Patient_ID,entity1,entity2,...

    """

    entity_fin = "'" + "','".join(entity) + "'"

    sql = """SELECT "Patient_ID","Key","Value" FROM examination_numerical2 WHERE "Key" IN ({0}) and "Billing_ID"='{1}'""".format(entity_fin,visit)
    try:
        df = pd.read_sql(sql, r)
        df = df.pivot_table(index="Patient_ID", columns="Key", values="Value", aggfunc=np.mean).reset_index()
        return df, None
    except Exception:
        return None, "Problem with load data from database"

def scatter_plot2(entities,visit,r):

    visit = "'" + "','".join(visit) + "'"
    entities = "'" + "','".join(entities) + "'"

    sql = """SELECT "Patient_ID","Billing_ID","Key","Value" from examination_numerical2 where "Billing_ID" in ({0}) and "Key" in ({1})""".format(visit,entities)


    df = pd.read_sql(sql, r)
    df = df.pivot_table(index=["Patient_ID","Billing_ID"], columns="Key", values="Value", aggfunc=np.mean).reset_index()

    return df, None



def get_cat_values(entity, subcategory,visit, r):
    """ Get categorical values from database

    get_cat_values use in scatter plot and coplots

    r: connection with database

    Returns
    -------
    df: DataFrame with columns Patient_ID,entity

    """

    subcategory_fin = "'" + "','".join(subcategory) + "'"

    sql = """SELECT "Patient_ID","Value" FROM examination_categorical2 WHERE "Key"= '{0}' 
            and "Value" IN ({1}) and "Billing_ID"='{2}'""".format(entity, subcategory_fin,visit)
    try:
        df = pd.read_sql(sql, r)
    except Exception:
        return None, "Problem with load data from database"
    if df.empty:
        return None, "The entity {} wasn't measured".format(entity)
    else:
        df.columns = ["Patient_ID", entity]
        return df, None




def get_cat_values_basic_stas(entity,visit, r):
    """ Get number of categorical values from database

    get_cat_values_basic_stas use only for basic_stas categorical

    r: connection with database

    Returns
    -------
    df: DataFrame with columns Key,count

    """
    try:
        entity_fin = "'" + "','".join(entity) + "'"
        sql = """SELECT "Key",count("Key") FROM examination_categorical2 WHERE "Key" IN ({0}) and "Billing_ID"='{1}'
                group by "Key" """.format(entity_fin,visit)
        df = pd.read_sql(sql, r)
        df = df.pivot_table(columns="Key", values="count")
        return df, None
    except Exception:
        return None, "Problem with load data from database"


def get_num_cat_values(entity_num, entity_cat, subcategory,visit, r):
    """ Retrieve categorical and numerical value

    get_num_cat_values use in histogram and boxplot

    r: connection with database

    Returns
    -------
    df: DataFrame with columns Patient_ID,entity_num,entity_cat
     """
    subcategory = "'" + "','".join(subcategory) + "'"
    visit = "'" + "','".join(visit) + "'"

    sql = """SELECT en."Patient_ID",en."Billing_ID",en."Value" as "{0}",ec."Value" as "{1}" FROM examination_numerical2 as en 
            left join examination_categorical2 as ec on en."Patient_ID" = ec."Patient_ID" 
            where en."Key" = '{0}' and ec."Key" = '{1}' and en."Billing_ID" IN ({3}) and ec."Billing_ID" IN ({3})
            and ec."Value" IN ({2}) order by ec."Value" """.format(entity_num, entity_cat, subcategory, visit)

    try:
        df = pd.read_sql(sql, r)
    except Exception:
        return None, "Problem with load data from database"
    if df.empty:
        return df, "The entity {0} or {1} wasn't measured".format(entity_num,entity_cat)
    else:
        return df, None


def get_num_cat_values_mean(entity_num, entity_cat, subcategory,how_plot, r):
    """ Retrieve categorical and numerical value

    get_num_cat_values use in histogram and boxplot

    r: connection with database

    Returns
    -------
    df: DataFrame with columns Patient_ID,entity_num,entity_cat
     """
    entity_num = "'" + "','".join(entity_num) + "'"
    subcategory = "'" + "','".join(subcategory) + "'"

    sql = """SELECT en."Billing_ID",en."Key",{3}(en."Value") as "Value",ec."Value" as "{1}" FROM examination_numerical2 as en 
            left join examination_categorical2 as ec on en."Patient_ID" = ec."Patient_ID" and en."Billing_ID" = ec."Billing_ID"
            where en."Key" IN ({0}) and ec."Key" = '{1}' and ec."Value" IN ({2}) group by en."Key",en."Billing_ID",ec."Value" order by en."Billing_ID" """.format(entity_num, entity_cat, subcategory,how_plot)

    try:
        df = pd.read_sql(sql, r)
    except Exception:
        return None, "Problem with load data from database"
    if df.empty:
        return df, "The entity {0} or {1} wasn't measured".format(entity_num, entity_cat)
    else:
        return df, None

def get_num_cat_values_mean_more_numeric(entity,how_plot, r):
    """ Get numerical values from numerical table  from database

    get_values use in scatter plot, heatmap, clustering, coplots

    r: connection with database

    Returns
    -------
    df: DataFrame with columns Patient_ID,entity1,entity2,...

    """

    entity_fin = "'" + "','".join(entity) + "'"

    sql = """SELECT "Billing_ID","Key",{1}("Value") as "Value" FROM examination_numerical2 WHERE "Key" IN ({0}) 
                group by "Billing_ID","Key" order by "Billing_ID","Key" """.format(entity_fin,how_plot)
    try:
        df = pd.read_sql(sql, r)
    except Exception:
        return None, "Problem with load data from database"
    if df.empty:
        return df, "{0} not measured".format(entity_fin)
    else:
        return df, None


def scatter_plot2(entities,visit,r):

    visit = "'" + "','".join(visit) + "'"
    entities = "'" + "','".join(entities) + "'"

    sql = """SELECT "Patient_ID","Billing_ID","Key","Value","count_visit" from examination_numerical2 where "Billing_ID" in ({0}) and "Key" in ({1}) """.format(visit,entities)


    df = pd.read_sql(sql, r)
    df = df.pivot_table(index=["Patient_ID","Billing_ID","count_visit"], columns="Key", values="Value", aggfunc=np.mean).reset_index()
    print(df)
    return df, None