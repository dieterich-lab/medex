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

    sql3 = """Select "Key" from name_type where "show" = '+' """

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
        sql = """Select distinct "Replicate":: int from examination order by "Replicate" """
        df = pd.read_sql(sql, r)
        df['Replicate']=df['Replicate'].astype(str)
        return df['Replicate']
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
    df: DataFrame with columns Patient_ID,Replicate,Key,instance,Value

    """
    import time
    entity_fin = "$$" + "$$,$$".join(entity) + "$$"
    entity_fin2 = '"'+'" text,"'.join(entity) + '" text'

    sql = """SELECT en."Transcript_ID",en."Replicate",en."Key",array_to_string(en."Value",';') as "Value" FROM examination_numerical as en WHERE en."Key" IN ({0})
     UNION
            SELECT ec."Transcript_ID",ec."Replicate",ec."Key",array_to_string(ec."Value",';') as "Value" FROM examination_categorical as ec WHERE ec."Key" IN ({0})""".format(entity_fin)

    sql2 = """SELECT * FROM crosstab('SELECT en."Transcript_ID",en."Replicate",en."Key",array_to_string(en."Value",'';'') as "Value" FROM examination_numerical as en WHERE en."Key" IN ({0})
        UNION
            SELECT ec."Transcript_ID",ec."Replicate",ec."Key",array_to_string(ec."Value",'';'') as "Value" FROM examination_categorical as ec WHERE ec."Key" IN ({0})',
            'SELECT "Key" FROM name_type WHERE "Key" IN ({0}) order by type,"Key"') 
            as ct ("Transcript_ID" text,"Replicate" text,{1})""".format(entity_fin,entity_fin2)


    sql3 = """SELECT * FROM crosstab('SELECT en."Transcript_ID",en."Replicate",en."Key",array_to_string(en."Value",'';'') as "Value" FROM examination as en WHERE en."Key" IN ({0})',
            'SELECT Distinct "Key" FROM examination WHERE "Key" IN ({0}) order by 1') 
            as ct ("Transcript_ID" text,"Replicate" text,{1})""".format(entity_fin,entity_fin2)


    try:

        if what_table == 'long':
            df = pd.read_sql(sql, r)

        else:
            df = pd.read_sql(sql2, r)

        return df, None
    except Exception:
        return None, "Problem with load data from database"




def get_num_values_basic_stats(entity,Replicate, r):
    """ Get numerical values from numerical table  from database

    get_numerical_values_basic_stats use in basic_stats

    r: connection with database

    Returns
    -------
    df: DataFrame with columns Patient_ID,Replicate,Key,instance,Value

    """

    entity_fin = "$$" + "$$,$$".join(entity) + "$$"
    Replicate = "'" + "','".join(Replicate) + "'"

    sql = """SELECT "Transcript_ID","Replicate","Key",instance,f."Value" FROM examination_numerical,unnest("Value") 
            WITH ordinality as f ("Value", instance)  WHERE "Key" IN ({0}) and "Replicate" IN ({1}) order by "Replicate" """.format(
        entity_fin, Replicate)
    try:
        df = pd.read_sql(sql, r)
    except Exception:
        return None, "Problem with load data from database"

    return df, None


def get_cat_values_basic_stas(entity,Replicate, r):
    """ Get number of categorical values from database

    get_cat_values_basic_stas use only for basic_stas categorical

    r: connection with database

    Returns
    -------
    df: DataFrame with columns Key,count

    """
    entity_fin = "$$" + "$$,$$".join(entity) + "$$"
    Replicate = "'" + "','".join(Replicate) + "'"

    sql = """SELECT "Key","Replicate",number,count("Key") FROM examination_categorical,array_length("Value",1) as f (number) WHERE "Key" IN ({0}) and "Replicate" IN ({1})
            group by "Replicate","Key",number """.format(entity_fin, Replicate)

    try:
        df = pd.read_sql(sql, r)
    except Exception:
        return None, "Problem with load data from database"

    return df,None


def get_values_scatter_plot(x_entity,y_entity,x_Replicate,y_Replicate, r):
    """ Get numerical values from numerical table  from database

    get_values use in scatter plot, coplot

    r: connection with database

    Returns
    -------
    df: DataFrame with columns Transcript_ID,entity1,entity2,...

    """

    sql = """SELECT "Transcript_ID",AVG(f."Value") as "{0}" FROM examination_numerical,unnest("Value") as f ("Value")  
            WHERE "Key" IN ('{0}') and "Replicate"= '{1}' Group by "Transcript_ID","Replicate","Key" order by "Replicate"  """.format(
        x_entity,x_Replicate)
    sql2 = """SELECT "Transcript_ID",AVG(f."Value") as "{0}" FROM examination_numerical,unnest("Value") as f ("Value")  
            WHERE "Key" IN ('{0}') and "Replicate"= '{1}' Group by "Transcript_ID","Replicate","Key" order by "Replicate" """.format(
        y_entity, y_Replicate)

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
            df = df1.merge(df2, on="Transcript_ID")
            return df, None
    except Exception:
        return None, "Problem with load data from database"


def get_cat_values(entity, subcategory,Replicate, r):
    """ Get categorical values from database

    get_cat_values use in scatter plot and coplots

    r: connection with database

    Returns
    -------
    df: DataFrame with columns Transcript_ID,entity

    """

    subcategory_fin = "$$" + "$$,$$".join(subcategory) + "$$"
    Replicate = "'" + "','".join(Replicate) + "'"

    sql = """SELECT "Transcript_ID",string_agg(distinct f."Value",',') FROM examination_categorical,unnest("Value") as f ("Value") WHERE "Key"= '{0}' 
    and f."Value" IN ({1})  and "Replicate" IN ({2}) Group by "Transcript_ID" order by string_agg(distinct f."Value",',')   """.format(entity, subcategory_fin,Replicate)

    try:
        df = pd.read_sql(sql, r)
    except Exception:
        return None, "Problem with load data from database"
    if df.empty or len(df) == 0:
        return None, "The entity {} wasn't measured".format(entity)
    else:
        df.columns = ["Transcript_ID", entity]
        return df, None


def get_cat_values_barchart(entity, subcategory,Replicate, r):
    """ Get number of subcategory values from database

    get_cat_values_barchart use only for barchart

    r: connection with database

    Returns
    -------
    df: DataFrame with columns Transcript_ID,Key,Value

    """


    Replicate = "'" + "','".join(Replicate) + "'"
    sql = """SELECT "Value","Replicate",count("Value") FROM examination_categorical WHERE "Key"='{0}' and "Replicate" IN ({2})
            and ARRAY{1} && "Value"  group by "Value","Replicate" """.format(entity, subcategory, Replicate)

    try:
        df = pd.read_sql(sql, r)
    except Exception:
        return None, "Problem with load data from database"
    if df.empty or len(df) == 0:
        return df, "{} not measured during this Replicate".format(entity)
    else:
        a =lambda x: ','.join(x)
        df['Value']=df['Value'].map(a)
        df.columns = [entity,'Replicate', 'count']
        print(df)
        return df,None


def get_num_cat_values(entity_num, entity_cat, subcategory,Replicate, r):
    """ Retrieve categorical and numerical value

    get_num_cat_values use in histogram and boxplot

    r: connection with database

    Returns
    -------
    df: DataFrame with columns Transcript_ID,entity_num,entity_cat
     """
    subcategory = "$$" + "$$,$$".join(subcategory) + "$$"
    Replicate = "'" + "','".join(Replicate) + "'"


    sql = """SELECT en."Transcript_ID",en."Replicate",AVG(a."Value") as "{0}",STRING_AGG(distinct f."Value", ',') as "{1}" FROM examination_numerical as en
                    left join examination_categorical as ec on en."Transcript_ID" = ec."Transcript_ID",unnest(en."Value") as a ("Value"),unnest(ec."Value") as f ("Value") 
                    where en."Key" = '{0}' and ec."Key" = '{1}' and en."Replicate" IN ({3}) and ec."Replicate" IN ({3})
                    and f."Value" IN ({2}) group by en."Transcript_ID",en."Replicate" order by en."Transcript_ID",en."Replicate" """.format(
        entity_num, entity_cat, subcategory, Replicate)

    try:
        df = pd.read_sql(sql, r)

    except Exception:
        return None, "Problem with load data from database"
    if df.empty or len(df) == 0:
        return df, "The entity {0} or {1} wasn't measured".format(entity_num,entity_cat)
    else:
        return df, None


def get_values_heatmap(entity,Replicate, r):
    """ Get numerical values from numerical table  from database

    get_values use in heatmap, clustering

    r: connection with database

    Returns
    -------
    df: DataFrame with columns Transcript_ID,entity1,entity2,...

    """

    entity_fin = "$$" + "$$,$$".join(entity) + "$$"

    sql = """SELECT "Transcript_ID","Replicate","Key",AVG(f."Value") as "Value" FROM examination_numerical, unnest("Value") as f("Value") WHERE "Key" IN ({0}) and "Replicate" in ('{1}') 
            Group by "Transcript_ID","Replicate","Key" """.format(entity_fin,Replicate)

    try:
        df = pd.read_sql(sql, r)
        df = df.pivot_table(index=["Transcript_ID"], columns="Key", values="Value", aggfunc=np.mean).reset_index()
        if df.empty or len(df) == 0:
            return df, "The entity wasn't measured"
        else:
            return df, None
    except Exception:
        return None, "Problem with load data from database"


def get_values_cat_heatmap(entity,Replicate, r):
    """ Get numerical values from numerical table  from database

    get_values use in heatmap, clustering

    r: connection with database

    Returns
    -------
    df: DataFrame with columns Transcript_ID,entity1,entity2,...

    """

    entity_fin = "$$" + "$$,$$".join(entity) + "$$"

    sql = """SELECT "Transcript_ID","Key","Value"[1] as "Value" FROM examination_categorical WHERE "Key" IN ({0}) """.format(entity_fin,Replicate)

    try:
        df = pd.read_sql(sql, r)
        df = df.pivot_table(index=["Transcript_ID"], columns="Key", values="Value", aggfunc=min).reset_index()
        print(df)
        if df.empty or len(df) == 0:
            return df, "The entity wasn't measured"
        else:
            return df, None
    except Exception:
        return None, "Problem with load data from database"



