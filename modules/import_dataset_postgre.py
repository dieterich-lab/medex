import psycopg2.extras
import numpy as np
from modules import config as con
import pandas as pd


# get your data into pandas
data = pd.read_csv('./dataset.csv', sep=',', names=["Patient_ID", "Billing_ID", "Date", "Time", "Key", "Value"])
df = pd.DataFrame(data)
df_value = df.pivot(index='Patient_ID', columns='Key', values='Value')

df_value.reset_index(inplace=True)

df_value['Delta0'] = df_value['Delta0'].astype(float)
df_value['Jitter_rel'] = df_value['Jitter_rel'].astype(float)
df_value['Jitter_abs'] = df_value['Jitter_abs'].astype(float)
df_value['Jitter_RAP'] = df_value['Jitter_RAP'].astype(float)
df_value['Jitter_PPQ'] = df_value['Jitter_PPQ'].astype(float)
df_value['Shim_loc'] = df_value['Shim_loc'].astype(float)
df_value['Shim_dB'] = df_value['Shim_dB'].astype(float)
df_value['Shim_APQ3'] = df_value['Shim_APQ3'].astype(float)
df_value['Shim_APQ5'] = df_value['Shim_APQ5'].astype(float)
df_value['Shi_APQ11'] = df_value['Shi_APQ11'].astype(float)
df_value['HNR05'] = df_value['HNR05'].astype(float)
df_value['HNR15'] = df_value['HNR15'].astype(float)
df_value['HNR25'] = df_value['HNR25'].astype(float)
df_value['HNR35'] = df_value['HNR35'].astype(float)
df_value['HNR38'] = df_value['HNR38'].astype(float)
df_value['RPDE'] = df_value['RPDE'].astype(float)
df_value['DFA'] = df_value['DFA'].astype(float)
df_value['PPE'] = df_value['PPE'].astype(float)
df_value['GNE'] = df_value['GNE'].astype(float)
df_value['MFCC0'] = df_value['MFCC0'].astype(float)
df_value['MFCC1'] = df_value['MFCC1'].astype(float)
df_value['MFCC2'] = df_value['MFCC2'].astype(float)
df_value['MFCC3'] = df_value['MFCC3'].astype(float)
df_value['MFCC4'] = df_value['MFCC4'].astype(float)
df_value['MFCC5'] = df_value['MFCC5'].astype(float)
df_value['MFCC6'] = df_value['MFCC6'].astype(float)
df_value['MFCC7'] = df_value['MFCC7'].astype(float)
df_value['MFCC8'] = df_value['MFCC8'].astype(float)
df_value['MFCC9'] = df_value['MFCC9'].astype(float)
df_value['MFCC10'] = df_value['MFCC10'].astype(float)
df_value['MFCC11'] = df_value['MFCC11'].astype(float)
df_value['MFCC12'] = df_value['MFCC12'].astype(float)
df_value['Delta0'] = df_value['Delta0'].astype(float)
df_value['Delta1'] = df_value['Delta1'].astype(float)
df_value['Delta2'] = df_value['Delta2'].astype(float)
df_value['Delta3'] = df_value['Delta3'].astype(float)
df_value['Delta4'] = df_value['Delta4'].astype(float)
df_value['Delta5'] = df_value['Delta5'].astype(float)
df_value['Delta6'] = df_value['Delta6'].astype(float)
df_value['Delta7'] = df_value['Delta7'].astype(float)
df_value['Delta8'] = df_value['Delta8'].astype(float)
df_value['Delta9'] = df_value['Delta9'].astype(float)
df_value['Delta10'] = df_value['Delta10'].astype(float)
df_value['Delta11'] = df_value['Delta11'].astype(float)
df_value['Delta12'] = df_value['Delta12'].astype(float)


cols = ",".join([str(i) for i in df_value.columns.tolist()])
cols = 'patient_id,' + cols
"""
"""
for i,row in df_value.iterrows():
    sql = "INSERT INTO patients_test ("+cols+") VALUES ({})".format(",".join(["%s" for _ in row]))

    conn = None
    try:
        # read database configuration
        params = con.config()
        # connect to the PostgreSQL database
        conn = psycopg2.connect(**params)
        # create a new cursor
        cur = conn.cursor()
        # execute the INSERT statement
        cur.execute(sql,tuple(row))
        # commit the changes to the database
        conn.commit()
        # close communication with the database
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()


"""
sql = "select column_name,data_type from INFORMATION_SCHEMA.COLUMNS where table_name = 'patients_test' and data_type = 'character varying'"
sql = "select column_name,data_type from INFORMATION_SCHEMA.COLUMNS where table_name = 'patients_test' and data_type = 'numeric'"
conn = None
try:
    # read database configuration
    params = con.config()
    # connect to the PostgreSQL database
    conn = psycopg2.connect(**params)
    # create a new cursor
    cur = conn.cursor()
    # execute the INSERT statement
    cur.execute(sql)
    rows = cur.fetchall()
    # commit the changes to the database
    conn.commit()
    # close communication with the database
    cur.close()
except (Exception, psycopg2.DatabaseError) as error:
    print(error)
finally:
    if conn is not None:
        conn.close()

m = np.array(rows)
# k = m.mean()
print(m)
"""