import pandas as pd
import os


def change_files_format():
    files = []
    entities_numerical, entities_categorical = [], []
    for r, d, f in os.walk('/home/magda/__git__/Fedex/DZKH/'):
        for i, file in enumerate(f):
            if '.csv' in file:
                df = pd.read_csv('/home/magda/__git__/Fedex/DZKH/' + file)
                if not df.empty:
                    drop_unnamed_columns(df)
                    df = join_value_and_unit_column(df)
                    df_without_na = pivot_and_remove_nan_value(df)
                    df_rename, entities_numerical, entities_categorical = \
                        rename_columns_with_unit(df_without_na, entities_numerical, entities_categorical)
                    df_rename.to_csv('/home/magda/Documents/FEDEX/data_goetthingen/data_merge/' + file, index=False, header=False)
                    files.append(file)
    create_entities_file(entities_categorical, entities_numerical)
    return files


def drop_unnamed_columns(df):
    unnamed_columns = [df.columns.get_loc(c) for c in list(df.filter(like='Unnamed').columns) if c in df]
    df.drop(df.columns[unnamed_columns], axis=1, inplace=True)


def join_value_and_unit_column(df):
    """ This function is responsible for combining the unit columns with the value columns"""
    """ Names of columns with units, should contain in their name einh !!!  """
    unit_name_list = list(df.filter(like='einh').columns)
    unit_indexes = [df.columns.get_loc(c) for c in unit_name_list if c in df]
    key_and_unit_indexes = [(x - 1, x) for x in unit_indexes]

    for i in range(len(unit_name_list)):
        column_name = list(df.columns[[key_and_unit_indexes[i][0]]])[0]
        df[column_name + '_unit'] = \
            df.iloc[:, key_and_unit_indexes[i][0]].map(str) + ' (' + \
                                    df.iloc[:, key_and_unit_indexes[i][1]] + ')'
    key_and_unit_indexes_list = [item for t in key_and_unit_indexes for item in t]
    df.drop(df.columns[key_and_unit_indexes_list], axis=1, inplace=True)
    return df


def pivot_and_remove_nan_value(df):
    df_melt = df.melt(
        id_vars=["mnppid", "mnpdocid", "mnpvisid", "mnpvispdt", "mnphide"],
        var_name="key",
        value_name="value")
    df_without_na = df_melt.dropna(subset=['value'])
    df_without_na = df_without_na[~df_without_na.value.str.startswith("nan", na=False)]
    df_without_na['value'] = df_without_na['value'].str.replace(',', '.')
    df_without_na.value = df_without_na.value.astype(str)
    return df_without_na


def rename_columns_with_unit(df_without_na, entities_numerical, entities_categorical):

    df_without_na.loc[df_without_na['key'].str.contains('unit'), 'key'] = \
        df_without_na.loc[df_without_na['key'].str.contains('unit'), 'key'] + ' ' + \
        df_without_na.loc[df_without_na['key'].str.contains('unit'), 'value'].str.split(' ', 1).str.get(1)

    df_without_na.loc[df_without_na['key'].str.contains('unit'), 'value'] = \
        df_without_na.loc[df_without_na['key'].str.contains('unit'), 'value'].str.split(' ', 1).str.get(0)

    df_without_na["key"] = df_without_na["key"].str.replace('_unit', '')
    df_without_na["key"] = df_without_na["key"].str.replace(',', ' ')

    entities_categorical = \
        entities_categorical + \
        list(df_without_na.loc[~df_without_na.value.apply(lambda x: x.replace('.', '').isdigit()),
                               'key'].drop_duplicates())
    entities_numerical = \
        entities_numerical + list(df_without_na.loc[df_without_na.value.apply(lambda x: x.replace('.', '').isdigit()),
                                                    'key'].drop_duplicates())
    return df_without_na, entities_numerical, entities_categorical


def create_entities_file(entities_categorical, entities_numerical):
    type_categorical = ['String'] * len(set(entities_categorical))
    type_numerical = ['Double'] * len(set(entities_numerical))
    df_entities_numerical = pd.DataFrame(list(zip(set(entities_numerical), type_numerical)), columns=['key', 'type'])
    df_entities_categorical = pd.DataFrame(list(zip(set(entities_categorical), type_categorical)), columns=['key', 'type'])
    result = pd.concat([df_entities_numerical, df_entities_categorical])
    result = result[~result.key.duplicated(keep='last')]
    result.to_csv('/home/magda/Documents/FEDEX/data_goetthingen/data_merge/import/entities.csv', index=False)


files_list = change_files_format()
print(files_list)
cmd = 'sed 1d /home/magda/Documents/FEDEX/data_goetthingen/data_merge/*.csv > ' \
      '/home/magda/Documents/FEDEX/data_goetthingen/data_merge/import/dataset.csv'
os.system(cmd)


def remove_not_harmonisierte_items():
    data = pd.read_csv('HarmonisierteItemsBasisregister_corrected.txt', header=None)
    df = pd.read_csv('/home/magda/Documents/FEDEX/data_goetthingen/data_merge/import/entities.csv')
    df['key'] = df['key'].str.split(' ').str.get(0)
    # list_entities_which_are_in_torch_and_transcript_data_but_not_in_HarmonisierteItemsBasisregister
    entities_to_remove = list(set(list(df['key'])) - set(list(data[0])))
    remove_not_harmonisierte_items_from_entities_file(entities_to_remove)
    remove_not_harmonisierte_items_from_dataset_file(entities_to_remove)


def remove_not_harmonisierte_items_from_dataset_file(entities_to_remove):
    df_dataset = pd.read_csv('/home/magda/Documents/FEDEX/data_goetthingen/data_merge/import/dataset.csv',
                             names=('id', 'case_id', 'visit', 'date', 'time', 'key', 'value'), low_memory=False)
    data_dataset = df_dataset.loc[~df_dataset['key'].isin(entities_to_remove)]
    data_dataset = data_dataset.loc[~data_dataset['key'].str.contains('lab_crp')]
    data_dataset = data_dataset.loc[~data_dataset['key'].str.contains('lab_mdrdgfr_tp')]
    data_dataset.to_csv('/home/magda/Documents/FEDEX/data_goetthingen/data_merge/import/dataset.csv', index=False,
                        header=None)


def remove_not_harmonisierte_items_from_entities_file(entities_to_remove):
    df_entities = pd.read_csv('/home/magda/Documents/FEDEX/data_goetthingen/data_merge/import/entities.csv')
    data_entities = df_entities.loc[~df_entities['key'].isin(entities_to_remove)]
    data_entities = data_entities.loc[~data_entities['key'].str.contains('lab_crp')]
    data_entities = data_entities.loc[~data_entities['key'].str.contains('lab_mdrdgfr_tp')]
    data_entities.to_csv('/home/magda/Documents/FEDEX/data_goetthingen/data_merge/import/entities.csv', index=False)


def change_visit_numbers_to_names():
    df = pd.read_csv('/home/magda/Documents/FEDEX/data_goetthingen/data_merge/import/dataset.csv',
                     names=('id', 'case_id', 'visit_id', 'date', 'time', 'key', 'value'), low_memory=False)
    df.loc[df['visit_id'].isin([2882, 22158, 2893]), 'visit'] = 'baseline'
    df = df[~df['visit_id'].isin([6685])]
    df.loc[df['visit_id'].isin([2883, 22156, 2890]), 'visit'] = '1 year followup'
    df.loc[df['visit_id'].isin([22157]), 'visit'] = '4 year followup'
    df.loc[df['visit_id'].isin([2891, 24470, 26263]), 'visit'] = '5 year followup'
    df_final = df[['id', 'case_id', 'visit', 'date', 'time', 'key', 'value']]
    df_final.to_csv('/home/magda/Documents/FEDEX/data_goetthingen/data_merge/import/dataset.csv', header=False,
                    index=False)


remove_not_harmonisierte_items()
change_visit_numbers_to_names()
