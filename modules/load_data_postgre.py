import pandas as pd
import numpy as np
from collections import ChainMap


def get_header(r):

    sql="Select * from header"
    df = pd.read_sql(sql, r)

    return df

def get_entities(r):
    sql = """SELECT "Key","description" FROM name_type order by "order" """

    try:
        df = pd.read_sql(sql, r)
        return df
    except Exception:
        return ["No data"]

def get_numerical_entities_scatter_plot(r):
    """ Retrieve numerical entities from PostgreSQL

    get_numeric_entities use in webserver

    r: connection with database

    Returns
    -------
    df["Key"]: list of all numerical entities
    """
    try:
        sql = """Select "Key","description" from name_type where type = 'Double' order by "Key" """
        df = pd.read_sql(sql, r)
        df = df[~df.Key.isin(['Tau.Measure','Chung.control1.pValue','Chung.control2.pValue','Chung.control3.pValue',
                              'Distance','DistanceMus','Expression.FPKM.Podocytes','Expression.FPKM.Glomerulus','Expression.FPKM.WholeKidney',
                              'Podocyte.Enrichment.Boerries_et_al_2013.log2FC','Podocyte.Enrichment.Boerries_et_al_2013.FDR'])]
        return df
    except Exception:
        return ["No data"]

def get_numerical_entities_histogram(r):
    """ Retrieve numerical entities from PostgreSQL

    get_numeric_entities use in webserver

    r: connection with database

    Returns
    -------
    df["Key"]: list of all numerical entities
    """
    try:
        sql = """Select "Key","description" from name_type where type = 'Double' order by "Key" """
        df = pd.read_sql(sql, r)
        df = df[~df.Key.isin(['Tau.Measure','Transcript.Length','Number.of.Exons','Chung.control1.pValue','Chung.control2.pValue','Chung.control3.pValue',
                              'Distance','DistanceMus','Expression.FPKM.Podocytes','Expression.FPKM.Glomerulus','Expression.FPKM.WholeKidney'
                                 ,'Podocyte.Enrichment.Boerries_et_al_2013.FDR'])]
        return df
    except Exception:
        return ["No data"]


def get_categorical_entities_scatter_plot(r):
    """ Retrieve numerical entities from PostgreSQL

    get_numeric_entities use in webserver

    r: connection with database

    Returns
    -------
    df["Key"]: list of all numerical entities
    """


    try:
        sql = """Select "Key","description" from name_type where "type" = 'String' order by "Key" """
        df = pd.read_sql(sql, r)
        df = df[~df.Key.isin(['ClosestNcTx','GeneID.EnsemblHSA.ProteinCoding','GeneID.EnsemblMMU.ProteinCoding','NcRNA.GeneID.HSA',
                              'GenomicCoordinates','GeneSymbol','GeneSymbol.HSA','NcRNASymbol','Conservation.by.Sequence','XLOCid'
                                 ,'ConservedBySequenceToHumanTX'])]
        return df
    except Exception:
        return ["No data"]

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


def get_measurement(r):
    """ Retrieve numerical entities from PostgreSQL

    get_numeric_entities use in websever

    r: connection with database

    Returns
    -------
    df["Key"]: list of all numerical entities
    """
    try:
        sql = """Select distinct "measurement":: int from examination order by "measurement" """
        df = pd.read_sql(sql, r)
        df['measurement']=df['measurement'].astype(str)
        return df['measurement']
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


def get_data(entity,what_table,filter,cat,r):
    """ Get numerical values from numerical table  from database

    get_numerical_values_basic_stats use in basic_stats

    r: connection with database

    Returns
    -------
    df: DataFrame with columns Name_ID,measurement,Key,instance,Value

    """

    entity_fin = "$$" + "$$,$$".join(entity) + "$$"
    entity_fin2 = '"'+'" text,"'.join(entity) + '" text'

    if not filter:
        sql = """SELECT en."Name_ID",en."measurement",en."Key",array_to_string(en."Value",';') as "Value" FROM examination_numerical as en WHERE en."Key" IN ({0}) 
         UNION
                SELECT ec."Name_ID",ec."measurement",ec."Key",array_to_string(ec."Value",';') as "Value" FROM examination_categorical as ec WHERE ec."Key" IN ({0})
                """.format(entity_fin, entity_fin2)

        sql3 = """SELECT * FROM crosstab('SELECT en."Name_ID",en."measurement",en."Key",array_to_string(en."Value",'';'') as "Value" FROM examination_numerical as en WHERE en."Key" IN ({0})
            UNION
                SELECT ec."Name_ID",ec."measurement",ec."Key",array_to_string(ec."Value",'';'') as "Value" FROM examination_categorical as ec WHERE ec."Key" IN ({0})',
                'SELECT "Key" FROM name_type WHERE "Key" IN ({0}) order by "order"') 
                as ct ("Name_ID" text,"measurement" text,{1}) """.format(entity_fin, entity_fin2)
    else:
        fil = [x.replace(" is ","\" in ('").replace(",","','") for x in filter]
        fil = '"'+"') and \"".join(fil) + "')"
        catu = "$$" + "$$,$$".join(cat) + "$$"
        catu_fin2 = '"' + '" text,"'.join(cat) + '" text'

        text = """SELECT "Name_ID" FROM crosstab('SELECT "Name_ID","Key",array_to_string("Value",'';'') as "Value" FROM examination_categorical WHERE "Key" IN ({0})')
                    AS CT ("Name_ID" text,{1}) where {2}""".format(catu, catu_fin2, fil)

        sql = """SELECT en."Name_ID",en."measurement",en."Key",array_to_string(en."Value",';') as "Value" FROM examination_numerical as en WHERE en."Key" IN ({0}) 
            and en."Name_ID" IN (""".format(entity_fin,entity_fin2) +text+""") 
         UNION
                SELECT ec."Name_ID",ec."measurement",ec."Key",array_to_string(ec."Value",';') as "Value" FROM examination_categorical as ec WHERE ec."Key" IN ({0}) and ec."Name_ID" IN (""".format(entity_fin,entity_fin2) +text+""")
                """.format(entity_fin,entity_fin2)


        sql3 = """SELECT * FROM crosstab('SELECT en."Name_ID",en."measurement",en."Key",array_to_string(en."Value",'';'') as "Value" FROM examination_numerical as en WHERE en."Key" IN ({0})
            UNION
                SELECT ec."Name_ID",ec."measurement",ec."Key",array_to_string(ec."Value",'';'') as "Value" FROM examination_categorical as ec WHERE ec."Key" IN ({0})',
                'SELECT "Key" FROM name_type WHERE "Key" IN ({0}) order by "order"') 
                as ct ("Name_ID" text,"measurement" text,{1}) where "Name_ID" in (""".format(entity_fin, entity_fin2) + text + """) """


    df = pd.read_sql(sql, r)
    try:
        if what_table == 'long':
            df = pd.read_sql(sql, r)
        else:
            df = pd.read_sql(sql3, r)

            #df = df1.merge(df2, on=["Name_ID","measurement"])

            # df = df3.merge(df4, on=["Name_ID", "GeneSymbol"])

        return df, None
    except Exception:
        return None, "Problem with load data from database"


def get_num_values_basic_stats(entity,measurement,filter,cat, r):
    """ Get numerical values from numerical table  from database

    get_numerical_values_basic_stats use in basic_stats

    r: connection with database

    Returns
    -------
    df: DataFrame with columns Name_ID,measurement,Key,instance,Value

    """

    entity_fin = "$$" + "$$,$$".join(entity) + "$$"
    measurement = "'" + "','".join(measurement) + "'"
    if not filter:
        sql = """SELECT "Key","measurement","instance",count(f."Value"),min(f."Value"),max(f."Value"),AVG(f."Value") as "mean",
        stddev(f."Value"),(stddev(f."Value")/sqrt(count(f."Value"))) as "stderr",(percentile_disc(0.5) within group (order by f."Value")) as median FROM examination_numerical,unnest("Value") WITH ordinality as f ("Value", instance)  
                WHERE "Key" IN ({0}) and "measurement" IN ({1}) group by "Key","measurement","instance" order by "Key","measurement","instance" """.format(
            entity_fin, measurement)
    else:
        fil = [x.replace(" is ","\" in ('").replace(",","','") for x in filter]
        fil = '"'+"') and \"".join(fil) + "')"
        catu = "$$" + "$$,$$".join(cat) + "$$"
        catu_fin2 = '"' + '" text,"'.join(cat) + '" text'
        text = """SELECT "Name_ID" FROM crosstab('SELECT "Name_ID","Key",array_to_string("Value",'';'') as "Value" FROM examination_categorical WHERE "Key" IN ({0})')
                    AS CT ("Name_ID" text,{1}) where {2}""".format(catu, catu_fin2, fil)


        sql = """SELECT "Key","measurement","instance",count(f."Value"),min(f."Value"),max(f."Value"),AVG(f."Value") as "mean",
        stddev(f."Value"),(stddev(f."Value")/sqrt(count(f."Value"))) as "stderr",(percentile_disc(0.5) within group (order by f."Value")) as median FROM examination_numerical,unnest("Value") WITH ordinality as f ("Value", instance)  
                WHERE "Key" IN ({0}) and "measurement" IN ({1}) and "Name_ID" in (""".format(entity_fin, measurement) + text + """)  group by "Key","measurement","instance" order by "Key","measurement","instance" """



    try:
        df = pd.read_sql(sql, r)
    except Exception:
        return None, "Problem with load data from database"

    return df, None


def get_cat_values_basic_stats(entity,measurement,filter,cat, r):
    """ Get number of categorical values from database

    get_cat_values_basic_stas use only for basic_stas categorical

    r: connection with database

    Returns
    -------
    df: DataFrame with columns Key,count

    """
    entity_fin = "$$" + "$$,$$".join(entity) + "$$"
    measurement = "'" + "','".join(measurement) + "'"

    if not filter:
        sql = """SELECT "Key","measurement",number,count("Key") FROM examination_categorical,array_length("Value",1) as f (number) WHERE "Key" IN ({0}) and "measurement" IN ({1})
                group by "measurement","Key",number """.format(entity_fin, measurement)
    else:
        fil = [x.replace(" is ","\" in ('").replace(",","','") for x in filter]
        fil = '"'+"') and \"".join(fil) + "')"
        catu = "$$" + "$$,$$".join(cat) + "$$"
        catu_fin2 = '"' + '" text,"'.join(cat) + '" text'
        text = """SELECT "Name_ID" FROM crosstab('SELECT "Name_ID","Key",array_to_string("Value",'';'') as "Value" FROM examination_categorical WHERE "Key" IN ({0})')
                    AS CT ("Name_ID" text,{1}) where {2}""".format(catu, catu_fin2, fil)


        sql = """SELECT "Key","measurement",number,count("Key") FROM examination_categorical,array_length("Value",1) as f (number) WHERE "Key" IN ({0}) and "measurement" IN ({1})
                and "Name_ID" in (""".format(entity_fin, measurement) + text + """)  group by "measurement","Key",number """


    try:
        df = pd.read_sql(sql, r)
    except Exception:
        return None, "Problem with load data from database"

    return df,None


def get_values_scatter_plot(x_entity,y_entity,x_measurement,y_measurement,filter,cat, r):
    """ Get numerical values from numerical table  from database

    get_values use in scatter plot, coplot

    r: connection with database

    Returns
    -------
    df: DataFrame with columns Name_ID,entity1,entity2,...

    """
    if not filter:
        sql = """SELECT "Name_ID",AVG(f."Value") as "{0}" FROM examination_numerical,unnest("Value") as f ("Value")  
                WHERE "Key" IN ('{0}') and "measurement"= '{1}' Group by "Name_ID","measurement","Key" order by "measurement"  """.format(
            x_entity,x_measurement)
        sql2 = """SELECT "Name_ID",AVG(f."Value") as "{0}" FROM examination_numerical,unnest("Value") as f ("Value")  
                WHERE "Key" IN ('{0}') and "measurement"= '{1}' Group by "Name_ID","measurement","Key" order by "measurement" """.format(
            y_entity, y_measurement)

        # load data with Gene symbol remove in case of Patient data
        sql3 = """SELECT en."Name_ID",min(fc."Value") as "GeneSymbol",AVG(f."Value") as "{0}" FROM examination_numerical as en left join examination_categorical as ec on en."Name_ID" = ec."Name_ID",unnest(en."Value") as f ("Value"),unnest(ec."Value") as fc ("Value")  
                WHERE en."Key" IN ('{0}') and en."measurement"= '{1}' and ec."Key" ='GeneSymbol' Group by en."Name_ID",ec."Key",en."measurement",en."Key" order by en."measurement"  """.format(
            x_entity,x_measurement)
        sql4 = """SELECT en."Name_ID",min(fc."Value") as "GeneSymbol",AVG(f."Value") as "{0}" FROM examination_numerical as en left join examination_categorical as ec on en."Name_ID" = ec."Name_ID",unnest(en."Value") as f ("Value"),unnest(ec."Value") as fc ("Value")  
                WHERE en."Key" IN ('{0}') and en."measurement"= '{1}' and ec."Key" ='GeneSymbol' Group by en."Name_ID",ec."Key",en."measurement",en."Key" order by en."measurement"  """.format(
            y_entity, y_measurement)
    else:
        fil = [x.replace(" is ","\" in ('").replace(",","','") for x in filter]
        fil = '"'+"') and \"".join(fil) + "')"
        catu = "$$" + "$$,$$".join(cat) + "$$"
        catu_fin2 = '"' + '" text,"'.join(cat) + '" text'
        text = """SELECT "Name_ID" FROM crosstab('SELECT "Name_ID","Key",array_to_string("Value",'';'') as "Value" FROM examination_categorical WHERE "Key" IN ({0})')
                    AS CT ("Name_ID" text,{1}) where {2}""".format(catu, catu_fin2, fil)


        sql = """SELECT "Name_ID",AVG(f."Value") as "{0}" FROM examination_numerical,unnest("Value") as f ("Value")  
                WHERE "Key" IN ('{0}') and "measurement"= '{1}' and "Name_ID" in (""".format(x_entity, x_measurement) + text + """) 
                Group by "Name_ID","measurement","Key" order by "measurement"  """
        sql2 = """SELECT "Name_ID",AVG(f."Value") as "{0}" FROM examination_numerical,unnest("Value") as f ("Value")  
                WHERE "Key" IN ('{0}') and "measurement"= '{1}' and "Name_ID" in (""".format(y_entity, y_measurement) + text + """) 
                Group by "Name_ID","measurement","Key" order by "measurement" """

        # load data with Gene symbol remove in case of Patient data
        sql3 = """SELECT en."Name_ID",min(fc."Value") as "GeneSymbol",AVG(f."Value") as "{0}" FROM examination_numerical as en left join examination_categorical as ec on en."Name_ID" = ec."Name_ID",unnest(en."Value") as f ("Value"),unnest(ec."Value") as fc ("Value")  
                WHERE en."Key" IN ('{0}') and en."measurement"= '{1}' and ec."Key" ='GeneSymbol' and en."Name_ID" in (""".format(x_entity, x_measurement) + text + """)
                 Group by en."Name_ID",ec."Key",en."measurement",en."Key" order by en."measurement"  """
        sql4 = """SELECT en."Name_ID",min(fc."Value") as "GeneSymbol",AVG(f."Value") as "{0}" FROM examination_numerical as en left join examination_categorical as ec on en."Name_ID" = ec."Name_ID",unnest(en."Value") as f ("Value"),unnest(ec."Value") as fc ("Value")  
                WHERE en."Key" IN ('{0}') and en."measurement"= '{1}' and ec."Key" ='GeneSymbol' and en."Name_ID" in (""".format(y_entity, y_measurement) + text + """)
                 Group by en."Name_ID",ec."Key",en."measurement",en."Key" order by en."measurement"  """


    try:
        #df1 = pd.read_sql(sql, r)
        #df2 = pd.read_sql(sql2, r)
        df3 = pd.read_sql(sql3, r)
        df4 = pd.read_sql(sql4, r)


        if len(df3) == 0:
            error = "Category {} is empty".format(x_entity)
            return None, error
        elif len(df4) == 0:
            error = "Category {} is empty".format(y_entity)
            return None, error
        else:
            #df = df1.merge(df2, on="Name_ID")
            df = df3.merge(df4, on=["Name_ID", "GeneSymbol"])
            return df, None
    except Exception:
        return None, "Problem with load data from database"


def get_cat_values(entity, subcategory,measurement,filter,cat, r):
    """ Get categorical values from database

    get_cat_values use in scatter plot and coplots

    r: connection with database

    Returns
    -------
    df: DataFrame with columns Name_ID,entity

    """

    subcategory_fin = "$$" + "$$,$$".join(subcategory) + "$$"
    measurement = "'" + "','".join(measurement) + "'"
    if not filter:
        sql = """SELECT "Name_ID",string_agg(distinct f."Value",',') FROM examination_categorical,unnest("Value") as f ("Value") WHERE "Key"= '{0}' 
        and f."Value" IN ({1})  and "measurement" IN ({2}) Group by "Name_ID" order by string_agg(distinct f."Value",',')""".format(entity, subcategory_fin,measurement)

    else:
        fil = [x.replace(" is ","\" in ('").replace(",","','") for x in filter]
        fil = '"'+"') and \"".join(fil) + "')"
        catu = "$$" + "$$,$$".join(cat) + "$$"
        catu_fin2 = '"' + '" text,"'.join(cat) + '" text'
        text = """SELECT "Name_ID" FROM crosstab('SELECT "Name_ID","Key",array_to_string("Value",'';'') as "Value" FROM examination_categorical WHERE "Key" IN ({0})')
                    AS CT ("Name_ID" text,{1}) where {2}""".format(catu, catu_fin2, fil)

        sql = """SELECT "Name_ID",string_agg(distinct f."Value",',') FROM examination_categorical,unnest("Value") as f ("Value") WHERE "Key"= '{0}' 
        and f."Value" IN ({1})  and "measurement" IN ({2} )and "Name_ID" in (""".format(entity, subcategory_fin,measurement) + text + """)
         Group by "Name_ID" order by string_agg(distinct f."Value",',')"""

    try:
        df = pd.read_sql(sql, r)
    except Exception:
        return None, "Problem with load data from database"
    if df.empty or len(df) == 0:
        return None, "The entity {} wasn't measured".format(entity)
    else:
        df.columns = ["Name_ID", entity]
        return df, None


def get_cat_values_barchart(entity, subcategory,measurement,filter,cat, r):
    """ Get number of subcategory values from database

    get_cat_values_barchart use only for barchart

    r: connection with database

    Returns
    -------
    df: DataFrame with columns Name_ID,Key,Value

    """

    measurement = "'" + "','".join(measurement) + "'"
    if not filter:
        sql = """SELECT "Value","measurement",count("Value") FROM examination_categorical WHERE "Key"='{0}' and "measurement" IN ({2})
                and ARRAY{1} && "Value"  group by "Value","measurement" """.format(entity, subcategory, measurement)
    else:
        fil = [x.replace(" is ","\" in ('").replace(",","','") for x in filter]
        fil = '"'+"') and \"".join(fil) + "')"
        catu = "$$" + "$$,$$".join(cat) + "$$"
        catu_fin2 = '"' + '" text,"'.join(cat) + '" text'
        text = """SELECT "Name_ID" FROM crosstab('SELECT "Name_ID","Key",array_to_string("Value",'';'') as "Value" FROM examination_categorical WHERE "Key" IN ({0})')
                    AS CT ("Name_ID" text,{1}) where {2}""".format(catu, catu_fin2, fil)

        sql = """SELECT "Value","measurement",count("Value") FROM examination_categorical WHERE "Key"='{0}' and "measurement" IN ({2})
                and ARRAY{1} && "Value" and "Name_ID" in (""".format(entity, subcategory, measurement) + text + """)  group by "Value","measurement" """

    try:
        df = pd.read_sql(sql, r)
    except Exception:
        return None, "Problem with load data from database"
    if df.empty or len(df) == 0:
        return df, "{} not measured during this measurement".format(entity)
    else:
        a =lambda x: ','.join(x)
        df['Value']=df['Value'].map(a)
        df.columns = [entity,'measurement', 'count']
        return df,None


def get_num_cat_values(entity_num, entity_cat, subcategory,measurement, filter, cat, r):
    """ Retrieve categorical and numerical value

    get_num_cat_values use in histogram and boxplot

    r: connection with database

    Returns
    -------
    df: DataFrame with columns Name_ID,entity_num,entity_cat
     """
    subcategory = "$$" + "$$,$$".join(subcategory) + "$$"
    measurement = "'" + "','".join(measurement) + "'"
    if not filter:
        sql = """SELECT en."Name_ID",en."measurement",AVG(a."Value") as "{0}",STRING_AGG(distinct f."Value", ',') as "{1}" FROM examination_numerical as en
                        left join examination_categorical as ec on en."Name_ID" = ec."Name_ID",unnest(en."Value") as a ("Value"),unnest(ec."Value") as f ("Value") 
                        where en."Key" = '{0}' and ec."Key" = '{1}' and en."measurement" IN ({3}) and ec."measurement" IN ({3})
                        and f."Value" IN ({2}) group by en."Name_ID",en."measurement" order by en."Name_ID",en."measurement" """.format(
            entity_num, entity_cat, subcategory, measurement)
    else:
        fil = [x.replace(" is ","\" in ('").replace(",","','") for x in filter]
        fil = '"'+"') and \"".join(fil) + "')"
        catu = "$$" + "$$,$$".join(cat) + "$$"
        catu_fin2 = '"' + '" text,"'.join(cat) + '" text'
        text = """SELECT "Name_ID" FROM crosstab('SELECT "Name_ID","Key",array_to_string("Value",'';'') as "Value" FROM examination_categorical WHERE "Key" IN ({0})')
                    AS CT ("Name_ID" text,{1}) where {2}""".format(catu, catu_fin2, fil)


        sql = """SELECT en."Name_ID",en."measurement",AVG(a."Value") as "{0}",STRING_AGG(distinct f."Value", ',') as "{1}" FROM examination_numerical as en
                        left join examination_categorical as ec on en."Name_ID" = ec."Name_ID",unnest(en."Value") as a ("Value"),unnest(ec."Value") as f ("Value") 
                        where en."Key" = '{0}' and ec."Key" = '{1}' and en."measurement" IN ({3}) and ec."measurement" IN ({3}) 
                        and f."Value" IN ({2}) and en."Name_ID" in (""".format(
            entity_num, entity_cat, subcategory, measurement)+ text +""") group by en."Name_ID",en."measurement" order by en."Name_ID",en."measurement" """

    try:
        df = pd.read_sql(sql, r)
    except Exception:
        return None, "Problem with load data from database"
    if df.empty or len(df) == 0:
        return df, "The entity {0} or {1} wasn't measured".format(entity_num,entity_cat)
    else:
        return df, None


def get_values_heatmap(entity,measurement,filter,cat, r):
    """ Get numerical values from numerical table  from database

    get_values use in heatmap, clustering

    r: connection with database

    Returns
    -------
    df: DataFrame with columns Name_ID,entity1,entity2,...

    """

    entity_fin = "$$" + "$$,$$".join(entity) + "$$"

    if not filter:
        sql = """SELECT "Name_ID","measurement","Key",AVG(f."Value") as "Value" FROM examination_numerical, unnest("Value") as f("Value") WHERE "Key" IN ({0}) and "measurement" in ('{1}') 
                Group by "Name_ID","measurement","Key" """.format(entity_fin,measurement)
    else:
        fil = [x.replace(" is ","\" in ('").replace(",","','") for x in filter]
        fil = '"'+"') and \"".join(fil) + "')"
        catu = "$$" + "$$,$$".join(cat) + "$$"
        catu_fin2 = '"' + '" text,"'.join(cat) + '" text'

        text = """SELECT "Name_ID" FROM crosstab('SELECT "Name_ID","Key",array_to_string("Value",'';'') as "Value" FROM examination_categorical WHERE "Key" IN ({0})')
                    AS CT ("Name_ID" text,{1}) where {2}""".format(catu, catu_fin2, fil)

        sql = """SELECT "Name_ID","measurement","Key",AVG(f."Value") as "Value" FROM examination_numerical, unnest("Value") as f("Value") WHERE "Key" IN ({0}) and "measurement" in ('{1}') and "Name_ID" in (""".format(entity_fin,measurement)+text+""")
                Group by "Name_ID","measurement","Key" """


    try:
        df = pd.read_sql(sql, r)
        df = df.pivot_table(index=["Name_ID"], columns="Key", values="Value", aggfunc=np.mean).reset_index()
        if df.empty or len(df) == 0:
            return df, "The entity wasn't measured"
        else:
            return df, None
    except Exception:
        return None, "Problem with load data from database"


def get_values_cat_heatmap(entity,measurement, r):
    """ Get numerical values from numerical table  from database

    get_values use in heatmap, clustering

    r: connection with database

    Returns
    -------
    df: DataFrame with columns Name_ID,entity1,entity2,...

    """

    entity_fin = "$$" + "$$,$$".join(entity) + "$$"

    sql = """SELECT "Name_ID","Key","Value"[1] as "Value" FROM examination_categorical WHERE "Key" IN ({0}) """.format(entity_fin,measurement)

    try:
        df = pd.read_sql(sql, r)
        df = df.pivot_table(index=["Name_ID"], columns="Key", values="Value", aggfunc=min).reset_index()
        if df.empty or len(df) == 0:
            return df, "The entity wasn't measured"
        else:
            return df, None
    except Exception:
        return None, "Problem with load data from database"


def get_values_clustering(entity, r):
    """ Get numerical values from numerical table  from database

    get_values use in heatmap, clustering

    r: connection with database

    Returns
    -------
    df: DataFrame with columns Name_ID,entity1,entity2,...

    """

    entity_fin = "$$" + "$$,$$".join(entity) + "$$"
    entity_fin2 = '"'+'" text,"'.join(entity) + '" text'

    sql2 = """SELECT * FROM crosstab('SELECT en."Name_ID",en."measurement",en."Key",array_to_string(en."Value",'';'') 
                as "Value" FROM examination_numerical as en WHERE en."Key" IN ({0}) 
        UNION
            SELECT ec."Name_ID",ec."measurement",ec."Key",array_to_string(ec."Value",'';'') as "Value" FROM examination_categorical as ec WHERE ec."Key" IN ({0})',
            'SELECT "Key" FROM name_type WHERE "Key" IN ({0}) order by type,"Key"') 
            as ct ("Name_ID" text,"measurement" text,{1})""".format(entity_fin,entity_fin2)
    try:
        df = pd.read_sql(sql2, r)

        return df, None

    except Exception:
        return None, "Problem with load data from database"

