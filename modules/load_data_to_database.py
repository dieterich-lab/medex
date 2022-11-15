from medex.services.database import get_db_session
from modules.models import TableNumerical, TableCategorical, TableDate, Patient
from sqlalchemy.sql import union, select, insert
import pandas as pd


def load_header(header):
    db_session = get_db_session()
    db_session.execute("INSERT INTO header values (%s, %s) ON CONFLICT DO NOTHING", [header[0], header[2]])
    db_session.commit()


def load_entities(entities):
    db_session = get_db_session()
    with open(entities, 'r') as in_file:
        head = next(in_file)
        i = 0
        for row in in_file:
            row = row.replace("  ", " ").replace("\n", "").split(",")
            if 'order' not in head:
                i += 1
                row = [str(i)] + row
            row = row + [''] * (7 - len(row))
            db_session.execute("INSERT INTO name_type values (%s, %s, %s, %s, %s, %s, %s) ON CONFLICT DO NOTHING", row)
    db_session.commit()
    in_file.close()
    df = pd.read_csv(entities)
    numerical_entities, date_entities = df[df['type'] == 'Double']['key'], df[df['type'] == 'Date']['key']
    numerical_entities, date_entities = numerical_entities.to_list(), date_entities.to_list()

    return numerical_entities, date_entities


def load_data(entities, dataset, header):
    """
    Load data from entities.csv, data.csv,header.csv files into examination table in Postgresql
    """
    # load data from header.csv file to header table
    db_session = get_db_session()
    numerical_entities, date_entities = load_entities(entities)
    with open(dataset, 'r', encoding="utf8", errors='ignore') as in_file:
        i = 0
        for row in in_file:
            i += 1
            row = row.rstrip().replace('"', "").replace("\n", "").split(",")
            if 'Visit' in header:
                line = [str(i)] + row[0:6] + [";".join([str(x) for x in row[6:]])]
            else:
                line = [str(i)] + row[0:2] + ['1'] + row[2:5] + [";".join([str(x) for x in row[5:]])]

            if len(line) < 7:
                print("This line doesn't have appropriate format:", line)
            else:
                line[6] = line[6].replace("  ", " ")
                if line[7].replace('.', '', 1).isdigit() and line[6] in numerical_entities:
                    db_session.execute("INSERT INTO examination_numerical values (%s,%s,%s,%s,%s,%s,%s,%s)", line)
                elif line[6] in date_entities:
                    db_session.execute("INSERT INTO examination_date values (%s,%s,%s,%s,%s,%s,%s,%s)", line)
                else:
                    db_session.execute("INSERT INTO examination_categorical values (%s,%s,%s,%s,%s,%s,%s,%s)", line)
    db_session.commit()
    in_file.close()


def patient_table():

    s_union = union(select(TableCategorical.name_id, TableCategorical.case_id),
                    select(TableNumerical.name_id, TableNumerical.case_id),
                    select(TableDate.name_id, TableDate.case_id)).subquery()
    s_select = select(s_union.c.name_id, s_union.c.case_id).group_by(s_union.c.name_id, s_union.c.case_id)
    sql_statement = insert(Patient).from_select(['name_id', 'case_id'], s_select)
    db_session = get_db_session()
    db_session.execute(sql_statement)
