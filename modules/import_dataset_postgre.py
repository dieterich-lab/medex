from sqlalchemy import create_engine
import pandas as pd

def load_data_to_table(dataset):
    # get your data into pandas
    data = pd.read_csv(dataset, sep=',', names=["Patient_ID", "Billing_ID", "Date", "Time", "Key", "Value"])
    df = pd.DataFrame(data)
    df_value = df.pivot(index='Patient_ID', columns='Key', values='Value')
    df_value.reset_index(inplace=True)


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
                elif isDigit(df_value[i][0]) == True and (df_value[i][0] == '0' or df_value[i][0] == '1'):
                    break
                elif isDigit(df_value[i][ii]) == True:
                    df_value[i] = df_value[i].astype(float)
                    break
                else:
                    break
        elif isDigit(df_value[i][0]) == True and (df_value[i][0] == '0' or df_value[i][0] == '1'):
            continue
        elif isDigit(df_value[i][0]) == True:
            df_value[i] = df_value[i].astype(float)



        engine = create_engine('postgresql+psycopg2://test:test@localhost:5428/example') # tu bede musiala zmienic jak zrobie container
        df_value.to_sql('patients_test2', con=engine, if_exists='replace')