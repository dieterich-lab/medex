import pandas as pd
import numpy as np


def get_categorical_entities(rdb):
    sql = """Select "Key" from name_type where "type" = 'String' """
    df= pd.read_sql(sql, rdb)

    return df['Key']


def get_values(entity, r):

    entity_fin = "'" + "','".join(entity) + "'"
    sql = """SELECT  "Patient_ID","Key","Value" FROM examination_numerical WHERE "Key" IN ({}) """.format(entity_fin)
    df = pd.read_sql(sql, r)
    df = df.pivot_table(index="Patient_ID", columns="Key", values="Value", aggfunc=np.mean).reset_index()
    return df


def get_cat_values(entity,r):
    entity_fin = "'" + "','".join(entity) + "'"
    sql = """SELECT  "Patient_ID","Key","Value" FROM examination_categorical WHERE "Key" IN ({}) """.format(entity_fin)
    df = pd.read_sql(sql, r)
    df = df.pivot_table(index="Patient_ID", columns="Key", values="Value", aggfunc=min).reset_index()
    return df


def get_num_cat_values(entity_num,entity_cat,r):
    entity = ",".join(entity_num)
    entity2 = ",".join(entity_cat)
    entity_finn = "'" + "','".join(entity_num) + "'"
    entity_finc = "'" + "','".join(entity_cat) + "'"
    sql = """SELECT  en."Patient_ID",en."Value" as "{0}",ec."Value" as "{3}" FROM examination_numerical as en 
            left join examination_categorical as ec on en."Patient_ID" = ec."Patient_ID" 
            where en."Key" in ({1}) and ec."Key" in ({2})""".format(entity,entity_finn,entity_finc,entity2)

    df = pd.read_sql(sql, r)
    return df





def get_numeric_entities(rdb):

    sql = """Select "Key" from name_type where type = 'Double'"""
    df= pd.read_sql(sql, rdb)

    return df['Key']

