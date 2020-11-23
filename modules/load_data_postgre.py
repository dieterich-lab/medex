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
    sql0 = """SELECT count(*) FROM examination_categorical"""
    sql1 = """Select "Key","description" from name_type where "type" = 'String' order by "Key" """
    # Retrieve categorical values with subcategories
    sql2 = """Select distinct "Key","Value"[1] from examination_categorical order by "Key","Value"[1] """

    sql3 = """Select "Key" from name_type where "link" = '+' """

    try:
        df0 = pd.read_sql(sql0, r)
        df0 = df0.iloc[0]['count']
        df1 = pd.read_sql(sql1, r)
        df = pd.read_sql(sql2, r)
        df3 = pd.read_sql(sql3, r)

        array = []

        # create dictionary with categories and subcategories
        for value in df1['Key']:
            dfr2 = {}
            df2 = df[df["Key"] == value]
            del df2['Key']
            dfr2[value] = list(df2['Value'])
            array.append(dfr2)
        df = dict(ChainMap(*array))
        return df1,df,df0,df3
    except Exception:
        return ["No data"],["No data"],["No data"],["No data"]


def get_numeric_entities(r):
    """ Retrieve numerical entities from PostgreSQL

    get_numeric_entities use in websever

    r: connection with database

    Returns
    -------
    df["Key"]: list of all numerical entities
    """
    try:
        sql0="""SELECT count(*) FROM examination_numerical"""

        sql = """Select "Key","description" from name_type where type = 'Double' order by "Key" """
        df = pd.read_sql(sql, r)
        df1 = pd.read_sql(sql0, r)
        df1=df1.iloc[0]['count']
        return df,df1
    except Exception:
        return ["No data"],["No data"]


def get_visit(r):
    """ Retrieve numerical entities from PostgreSQL

    get_numeric_entities use in websever

    r: connection with database

    Returns
    -------
    df["Key"]: list of all numerical entities
    """
    try:
        sql = """Select distinct "Visit":: int from examination order by "Visit" """
        df = pd.read_sql(sql, r)
        df['Visit']=df['Visit'].astype(str)
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


def get_data2(entity,what_table,r):
    """ Get numerical values from numerical table  from database

    get_numerical_values_basic_stats use in basic_stats

    r: connection with database

    Returns
    -------
    df: DataFrame with columns Patient_ID,Visit,Key,instance,Value

    """
    import time
    entity_fin = "$$" + "$$,$$".join(entity) + "$$"
    entity_fin2 = '"'+'" text,"'.join(entity) + '" text'

    sql = """SELECT en."Patient_ID",en."Visit",en."Key",array_to_string(en."Value",';') as "Value" FROM examination_numerical as en WHERE en."Key" IN ({0})
     UNION
            SELECT ec."Patient_ID",ec."Visit",ec."Key",array_to_string(ec."Value",';') as "Value" FROM examination_categorical as ec WHERE ec."Key" IN ({0})""".format(entity_fin)

    sql2 = """SELECT * FROM crosstab('SELECT en."Patient_ID",en."Visit",en."Key",array_to_string(en."Value",'';'') as "Value" FROM examination_numerical as en WHERE en."Key" IN ({0})
        UNION
            SELECT ec."Patient_ID",ec."Visit",ec."Key",array_to_string(ec."Value",'';'') as "Value" FROM examination_categorical as ec WHERE ec."Key" IN ({0})',
            'SELECT "Key" FROM name_type WHERE "Key" IN ({0}) order by type,"Key"') 
            as ct ("Patient_ID" text,"Visit" text,{1})""".format(entity_fin,entity_fin2)


    sql3 = """SELECT * FROM crosstab('SELECT en."Patient_ID",en."Visit",en."Key",array_to_string(en."Value",'';'') as "Value" FROM examination as en WHERE en."Key" IN ({0})',
            'SELECT Distinct "Key" FROM examination WHERE "Key" IN ({0}) order by 1') 
            as ct ("Patient_ID" text,"Visit" text,{1})""".format(entity_fin,entity_fin2)


    try:

        if what_table == 'long':
            df = pd.read_sql(sql, r)

        else:
            df = pd.read_sql(sql2, r)

        return df, None
    except Exception:
        return None, "Problem with load data from database"




def get_num_values_basic_stats(entity,visit, r):
    """ Get numerical values from numerical table  from database

    get_numerical_values_basic_stats use in basic_stats

    r: connection with database

    Returns
    -------
    df: DataFrame with columns Patient_ID,Visit,Key,instance,Value

    """

    entity_fin = "$$" + "$$,$$".join(entity) + "$$"
    visit = "'" + "','".join(visit) + "'"

    sql = """SELECT "Patient_ID","Visit","Key",instance,f."Value" FROM examination_numerical,unnest("Value") 
            WITH ordinality as f ("Value", instance)  WHERE "Key" IN ({0}) and "Visit" IN ({1}) order by "Visit" """.format(
        entity_fin, visit)
    try:
        df = pd.read_sql(sql, r)
    except Exception:
        return None, "Problem with load data from database"

    return df, None


def get_cat_values_basic_stas(entity,visit, r):
    """ Get number of categorical values from database

    get_cat_values_basic_stas use only for basic_stas categorical

    r: connection with database

    Returns
    -------
    df: DataFrame with columns Key,count

    """
    entity_fin = "$$" + "$$,$$".join(entity) + "$$"
    visit = "'" + "','".join(visit) + "'"

    sql = """SELECT "Key","Visit",number,count("Key") FROM examination_categorical,array_length("Value",1) as f (number) WHERE "Key" IN ({0}) and "Visit" IN ({1})
            group by "Visit","Key",number """.format(entity_fin, visit)

    try:
        df = pd.read_sql(sql, r)
    except Exception:
        return None, "Problem with load data from database"

    return df,None


def get_values_scatter_plot(x_entity,y_entity,x_visit,y_visit, r):
    """ Get numerical values from numerical table  from database

    get_values use in scatter plot, coplot

    r: connection with database

    Returns
    -------
    df: DataFrame with columns Patient_ID,entity1,entity2,...

    """

    sql = """SELECT "Patient_ID",AVG(f."Value") as "{0}" FROM examination_numerical,unnest("Value") as f ("Value")  
            WHERE "Key" IN ('{0}') and "Visit"= '{1}' Group by "Patient_ID","Visit","Key" order by "Visit"  """.format(
        x_entity,x_visit)
    sql2 = """SELECT "Patient_ID",AVG(f."Value") as "{0}" FROM examination_numerical,unnest("Value") as f ("Value")  
            WHERE "Key" IN ('{0}') and "Visit"= '{1}' Group by "Patient_ID","Visit","Key" order by "Visit" """.format(
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


def get_cat_values(entity, subcategory,visit, r):
    """ Get categorical values from database

    get_cat_values use in scatter plot and coplots

    r: connection with database

    Returns
    -------
    df: DataFrame with columns Patient_ID,entity

    """

    subcategory_fin = "$$" + "$$,$$".join(subcategory) + "$$"
    visit = "'" + "','".join(visit) + "'"

    sql = """SELECT "Patient_ID",string_agg(distinct f."Value",',') FROM examination_categorical,unnest("Value") as f ("Value") WHERE "Key"= '{0}' 
    and f."Value" IN ({1})  and "Visit" IN ({2}) Group by "Patient_ID" order by string_agg(distinct f."Value",',')   """.format(entity, subcategory_fin,visit)

    try:
        df = pd.read_sql(sql, r)
    except Exception:
        return None, "Problem with load data from database"
    if df.empty or len(df) == 0:
        return None, "The entity {} wasn't measured".format(entity)
    else:
        df.columns = ["Patient_ID", entity]
        return df, None


def get_cat_values_barchart(entity, subcategory,visit, r):
    """ Get number of subcategory values from database

    get_cat_values_barchart use only for barchart

    r: connection with database

    Returns
    -------
    df: DataFrame with columns Patient_ID,Key,Value

    """


    visit = "'" + "','".join(visit) + "'"
    sql = """SELECT "Value","Visit",count("Value") FROM examination_categorical WHERE "Key"='{0}' and "Visit" IN ({2})
            and ARRAY{1} && "Value"  group by "Value","Visit" """.format(entity, subcategory, visit)

    try:
        df = pd.read_sql(sql, r)
    except Exception:
        return None, "Problem with load data from database"
    if df.empty or len(df) == 0:
        return df, "{} not measured during this visit".format(entity)
    else:
        a =lambda x: ','.join(x)
        df['Value']=df['Value'].map(a)
        df.columns = [entity,'Visit', 'count']
        print(df)
        return df,None


def get_num_cat_values(entity_num, entity_cat, subcategory,visit, r):
    """ Retrieve categorical and numerical value

    get_num_cat_values use in histogram and boxplot

    r: connection with database

    Returns
    -------
    df: DataFrame with columns Patient_ID,entity_num,entity_cat
     """
    subcategory = "$$" + "$$,$$".join(subcategory) + "$$"
    visit = "'" + "','".join(visit) + "'"


    sql = """SELECT en."Patient_ID",en."Visit",AVG(a."Value") as "{0}",STRING_AGG(distinct f."Value", ',') as "{1}" FROM examination_numerical as en
                    left join examination_categorical as ec on en."Patient_ID" = ec."Patient_ID",unnest(en."Value") as a ("Value"),unnest(ec."Value") as f ("Value") 
                    where en."Key" = '{0}' and ec."Key" = '{1}' and en."Visit" IN ({3}) and ec."Visit" IN ({3})
                    and f."Value" IN ({2}) group by en."Patient_ID",en."Visit" order by en."Patient_ID",en."Visit" """.format(
        entity_num, entity_cat, subcategory, visit)

    try:
        df = pd.read_sql(sql, r)

    except Exception:
        return None, "Problem with load data from database"
    if df.empty or len(df) == 0:
        return df, "The entity {0} or {1} wasn't measured".format(entity_num,entity_cat)
    else:
        return df, None


def get_values_heatmap(entity,visit, r):
    """ Get numerical values from numerical table  from database

    get_values use in heatmap, clustering

    r: connection with database

    Returns
    -------
    df: DataFrame with columns Patient_ID,entity1,entity2,...

    """

    entity_fin = "$$" + "$$,$$".join(entity) + "$$"

    sql = """SELECT "Patient_ID","Visit","Key",AVG(f."Value") as "Value" FROM examination_numerical, unnest("Value") as f("Value") WHERE "Key" IN ({0}) and "Visit" in ('{1}') 
            Group by "Patient_ID","Visit","Key" """.format(entity_fin,visit)

    try:
        df = pd.read_sql(sql, r)
        df = df.pivot_table(index=["Patient_ID"], columns="Key", values="Value", aggfunc=np.mean).reset_index()
        if df.empty or len(df) == 0:
            return df, "The entity wasn't measured"
        else:
            return df, None
    except Exception:
        return None, "Problem with load data from database"


def get_values_cat_heatmap(entity,visit, r):
    """ Get numerical values from numerical table  from database

    get_values use in heatmap, clustering

    r: connection with database

    Returns
    -------
    df: DataFrame with columns Patient_ID,entity1,entity2,...

    """

    entity_fin = "$$" + "$$,$$".join(entity) + "$$"

    sql = """SELECT "Patient_ID","Key","Value"[1] as "Value" FROM examination_categoricalWHERE "Key" IN ({0}) """.format(entity_fin,visit)

    try:
        df = pd.read_sql(sql, r)
        df = df.pivot_table(index=["Patient_ID"], columns="Key", values="Value", aggfunc=np.mean).reset_index()
        if df.empty or len(df) == 0:
            return df, "The entity wasn't measured"
        else:
            return df, None
    except Exception:
        return None, "Problem with load data from database"

