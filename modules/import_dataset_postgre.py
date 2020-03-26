from sqlalchemy import create_engine
import psycopg2.extras
from modules import config as con
import pandas as pd


# get your data into pandas
data = pd.read_csv('../import/cardio_testdata_long_format.txt', sep=',', names=["Patient_ID", "Billing_ID", "Date", "Time", "Key", "Value"])
df = pd.DataFrame(data)
df_value = df.pivot(index='Patient_ID', columns='Key', values='Value')
df_value.reset_index(inplace=True)

#print(df_value['basis_kreatinin_baseline'])
#print(df_value.dtypes)

def isDigit(x):
    try:
        float(x)
        return True
    except ValueError:
        return False


for i in df_value.columns.tolist():
    if pd.isna(df_value[i][0]):
        ii=0
        while ii < len(df_value.index)-1:
            ii+=1
            if pd.isna(df_value[i][ii]):
                continue
            elif isDigit(df_value[i][ii]) == True:
                df_value[i] = df_value[i].astype(float)
                break
            else:
                break
    elif isDigit(df_value[i][0]) == True and (df_value[i][0] == 0 or df_value[i][0] == 1):
        continue
    elif isDigit(df_value[i][0]) == True:
        df_value[i] = df_value[i].astype(float)



engine = create_engine('postgresql+psycopg2://postgres:12345@localhost:5432/test_patient')
df_value.to_sql('patients_test2', con=engine)



"""
cols = ",".join([str(i) for i in df_value.columns.tolist()])
cols = 'Patient_id,' + cols

for i,row in df_value.iterrows():
    
    sql = "INSERT INTO patients_test2 ("+cols+") VALUES ({})".format(",".join(["%s" for _ in row]))

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

