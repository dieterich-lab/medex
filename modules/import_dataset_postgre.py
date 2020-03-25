import psycopg2.extras
from modules import config as con
import pandas as pd


# get your data into pandas
data = pd.read_csv('../import/dataset.csv', sep=',', names=["Patient_ID", "Billing_ID", "Date", "Time", "Key", "Value"])
df = pd.DataFrame(data)
df_value = df.pivot(index='Patient_ID', columns='Key', values='Value')
df_value.reset_index(inplace=True)



for i in df_value.columns.tolist():
    df_value[i] = df_value[i].str.replace(".", "")
    if df_value[i][0].isdigit() == True:
        df_value[i] = df_value[i].astype(float)





cols = ",".join([str(i) for i in df_value.columns.tolist()])
cols = 'patient_id,' + cols

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


