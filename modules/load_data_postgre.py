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
    sql1 = """Select "Key","description" from name_type where "type" = 'String' order by "Key" """

    # Retrieve categorical values with subcategories
    sql2 = """Select distinct "Key","Value"[1] from examination_categorical order by "Key","Value"[1] """
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
        return df1,df
    except Exception:
        return ["No data"],["No data"]




def get_numeric_entities(r):
    """ Retrieve numerical entities from PostgreSQL

    get_numeric_entities use in websever

    r: connection with database

    Returns
    -------
    df["Key"]: list of all numerical entities
    """
    try:
        sql = """Select "Key","description" from name_type where type = 'Double' order by "Key" """
        df = pd.read_sql(sql, r)
        return df
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
        sql = """Select distinct "Visit" from examination order by "Visit" """
        df = pd.read_sql(sql, r)
        return df['Visit']
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

    sql = """SELECT "Patient_ID","Visit","Key","Value"[1] FROM examination_numerical WHERE "Key" IN ({0}) and "Visit" IN ({1}) order by "Visit" """.format(entity_fin,visit)

    try:
        df = pd.read_sql(sql, r)
    except Exception:
        return None, "Problem with load data from database"
    if df.empty:
        return df, "{} not measured during this visit".format(entity_fin)
    else:
        df = df.pivot_table(index=["Patient_ID", "Visit"], columns="Key", values="Value",
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

    sql = """SELECT "Visit","Key",count("Key") FROM examination_categorical WHERE "Key" IN ({0}) and "Visit" IN ({1})
            group by "Visit","Key" """.format(entity_fin, visit)
    try:
        df = pd.read_sql(sql, r)
    except Exception:
        return None, "Problem with load data from database"
    if df.empty:
        return df, "{} not measured during this visit".format(entity_fin)
    else:
        df = df.pivot_table(index="Visit", columns="Key", values="count")
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
    sql = """SELECT "Value"[1],"Visit",count("Value"[1]) FROM examination_categorical WHERE "Key"='{0}' and "Visit" IN ({2})
            and "Value"[1] IN ({1}) group by "Value"[1],"Visit" """.format(entity, subcategory, visit)
    try:
        df = pd.read_sql(sql, r)
    except Exception:
        return None, "Problem with load data from database"
    if df.empty:
        return df, "{} not measured during this visit".format(entity)
    else:
        df.columns = [entity,'Visit', 'count']
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

    sql = """SELECT count("Patient_ID"),"Visit","Key" 
                from examination_categorical  where "Key" IN ({}) and "Visit" IN ({}) group by "Visit","Key" """.format(entities,visit)
    sql2 = """SELECT count("Patient_ID"),"Visit","Key" 
                    from examination_numerical  where "Key" IN ({}) and "Visit" IN ({}) group by "Visit","Key" """.format(entities,visit)
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






def get_values(x_entity,y_entity,x_visit,y_visit, r):
    """ Get numerical values from numerical table  from database

    get_values use in scatter basic_stats,plot, heatmap, clustering, coplots

    r: connection with database

    Returns
    -------
    df: DataFrame with columns Patient_ID,entity1,entity2,...

    """

#    entity_fin = "'" + "','".join(entity) + "'"

    sql = """SELECT "Patient_ID","Value"[1] as {0} FROM examination_numerical WHERE "Key" IN ('{0}') and "Visit"='{1}'""".format(x_entity,x_visit)
    sql2 = """SELECT "Patient_ID","Value"[1] as {0} FROM examination_numerical WHERE "Key" IN ('{0}') and "Visit"='{1}'""".format(
        y_entity, y_visit)
    try:
        df1 = pd.read_sql(sql, r)
        df2 = pd.read_sql(sql2, r)
        if len(df1) == 0:
            error = "Category {} is empty".format(x_entity)
            return None, error
        elif len(df2) == 0:
            error = "Category {} is empty".format(y_entity)
            return None, error
        else :
            df = df1.merge(df2, on="Patient_ID")
            return df, None
    except Exception:
        return None, "Problem with load data from database"



def get_values_heatmap(entity,visit, r):
    """ Get numerical values from numerical table  from database

    get_values use in scatter basic_stats,plot, heatmap, clustering, coplots

    r: connection with database

    Returns
    -------
    df: DataFrame with columns Patient_ID,entity1,entity2,...

    """

    entity_fin = "'" + "','".join(entity) + "'"

    sql = """SELECT "Patient_ID","Visit","Key","Value"[1] FROM examination_numerical WHERE "Key" IN ({0}) and "Visit" in ('{1}') """.format(entity_fin,visit)

    try:
        df = pd.read_sql(sql, r)
        df = df.pivot_table(index=["Patient_ID"], columns="Key", values="Value", aggfunc=np.mean).reset_index()
        return df, None
    except Exception:
        return None, "Problem with load data from database"

def scatter_plot2(entities,visit,r):

    visit = "'" + "','".join(visit) + "'"
    entities = "'" + "','".join(entities) + "'"

    sql = """SELECT "Patient_ID","Visit","Key","Value"[1] from examination_numerical where "Visit" in ({0}) and "Key" in ({1})""".format(visit,entities)


    df = pd.read_sql(sql, r)
    df = df.pivot_table(index=["Patient_ID","Visit"], columns="Key", values="Value", aggfunc=np.mean).reset_index()

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
    visit = "'" + "','".join(visit) + "'"

    sql = """SELECT "Patient_ID","Value"[1] FROM examination_categorical WHERE "Key"= '{0}' 
            and "Value"[1] IN ({1}) and "Visit" IN ({2})""".format(entity, subcategory_fin,visit)
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
        sql = """SELECT "Key",count("Key") FROM examination_categorical WHERE "Key" IN ({0}) and "Visit"='{1}'
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

    sql = """SELECT en."Patient_ID",en."Visit",en."Value"[1] as "{0}",ec."Value"[1] as "{1}" FROM examination_numerical as en 
            left join examination_categorical as ec on en."Patient_ID" = ec."Patient_ID" 
            where en."Key" = '{0}' and ec."Key" = '{1}' and en."Visit" IN ({3}) and ec."Visit" IN ({3})
            and ec."Value"[1] IN ({2}) order by ec."Value"[1] """.format(entity_num, entity_cat, subcategory, visit)

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

    sql = """SELECT en."Visit",en."Key",{3}(en."Value"[1]) as "Value"[1],ec."Value"[1] as "{1}" FROM examination_numerical as en 
            left join examination_categorical as ec on en."Patient_ID" = ec."Patient_ID" and en."Visit" = ec."Visit"
            where en."Key" IN ({0}) and ec."Key" = '{1}' and ec."Value"[1] IN ({2}) group by en."Key",en."Visit",ec."Value"[1] order by en."Visit" """.format(entity_num, entity_cat, subcategory,how_plot)

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

    sql = """SELECT "Visit","Key",{1}("Value"[1]) as "Value"[1] FROM examination_numerical WHERE "Key" IN ({0}) 
                group by "Visit","Key" order by "Visit","Key" """.format(entity_fin,how_plot)
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

    sql = """SELECT "Patient_ID","Visit","Key","Value"[1],"count_visit" from examination_numerical where "Visit" in ({0}) and "Key" in ({1}) """.format(visit,entities)


    df = pd.read_sql(sql, r)
    df = df.pivot_table(index=["Patient_ID","Visit","count_visit"], columns="Key", values="Value", aggfunc=np.mean).reset_index()
    print(df)
    return df, None