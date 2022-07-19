from modules.models import TableNumerical, TableCategorical, TableDate, Header, Patient
from sqlalchemy.sql import union, select, distinct, join, label
from sqlalchemy.orm import aliased
from sqlalchemy import String, and_, literal_column, asc, text, desc, func
import pandas as pd
import datetime
from collections import ChainMap


def get_header(r):
    sql = select(Header)
    try:
        df = pd.read_sql(sql, r)
        name_id, measurement_name = df['name_id'][0], df['measurement'][0]
    except (Exception,):
        name_id, measurement_name = 'name_id', 'measurement'
    return name_id, measurement_name


def get_database_information(r):
    size_num_table = """SELECT count(*) FROM examination_numerical"""
    size_date_table = """SELECT count(*) FROM examination_date"""
    size_cat_table = """SELECT count(*) FROM examination_categorical"""
    try:
        size_num_tab, size_date_tab, size_cat_tab = pd.read_sql(size_num_table, r), pd.read_sql(size_date_table, r), \
                                                    pd.read_sql(size_cat_table, r)
        size_num_tab, size_date_tab, size_cat_tab = \
            size_num_tab.iloc[0]['count'], size_date_tab.iloc[0]['count'],\
            size_cat_tab.iloc[0]['count']
    except (Exception,):
        size_num_tab, size_date_tab, size_cat_tab = 0, 0, 0
    return size_num_tab, size_date_tab, size_cat_tab
        

def get_date(r):
    sql = """ SELECT min("date"),max("date") FROM examination_numerical """
    try:
        df = pd.read_sql(sql, r)
        start_date = datetime.datetime.strptime(df['min'][0], '%Y-%m-%d').timestamp() * 1000
        end_date = datetime.datetime.strptime(df['max'][0], '%Y-%m-%d').timestamp() * 1000
    except (Exception,):
        now = datetime.datetime.now()
        start_date = datetime.datetime.timestamp(now - datetime.timedelta(days=365.24*100)) * 1000
        end_date = datetime.datetime.timestamp(now) * 1000
    return start_date, end_date


def patient(r):
    sql = """SELECT * FROM Patient"""
    try:
        df = pd.read_sql(sql, r)
        return df['name_id'], None
    except (Exception,):
        return None, "Problem with load data from database"


def get_entities(r):
    all_entities = """SELECT key,type,description,synonym FROM name_type ORDER BY orders """
    try:
        entities = pd.read_sql(all_entities, r)
        entities = entities.replace([None], ' ')
        num_entities = entities[entities['type'] == 'Double'].drop(columns=['type'])
        cat_entities = entities[entities['type'] == 'String'].drop(columns=['type'])
        date_entities = entities[entities['type'] == 'Date'].drop(columns=['type'])
        entities = entities.drop(columns=['type'])

        all_num_entities, all_cat_entities = num_entities.to_dict('index'), cat_entities.to_dict('index')
        all_date_entities, all_entities = date_entities.to_dict('index'), entities.to_dict('index')
        length = (str(len(num_entities)), str(len(cat_entities)), str(len(date_entities)))
    except (Exception,):
        all_entities, all_num_entities, all_cat_entities, all_date_entities, length = {}, {}, {}, {}, ('0', '0', '0')
    return all_entities, all_num_entities, all_cat_entities, all_date_entities, length


def min_max_value_numeric_entities(r):
    min_max = """SELECT key,max(value),min(value) FROM examination_numerical GROUP BY key """
    try:
        df_min_max = pd.read_sql(min_max, r)
        df_min_max = df_min_max.set_index('key')
        df_min_max = df_min_max.to_dict('index')
    except (Exception,):
        df_min_max = pd.DataFrame()
        df_min_max = df_min_max.to_dict('index')
    return df_min_max


def get_subcategories_from_categorical_entities(r):
    all_subcategories = """SELECT DISTINCT key,value FROM examination_categorical ORDER by key """
    try:
        subcategories = pd.read_sql(all_subcategories, r)
        entities = subcategories['key'].unique()
        array = []
        df_subcategories = {}
        # create dictionary with categories and subcategories
        for value in entities:
            df = subcategories[subcategories['key'] == value]
            del df['key']
            df_subcategories[value] = list(df['value'])
            array.append(df_subcategories)

        df_subcategories = dict(ChainMap(*array))
    except (Exception,):
        df_subcategories = {}
    return df_subcategories


def get_measurement(r):
    sql = """SELECT DISTINCT measurement:: int FROM examination_numerical ORDER BY measurement """
    try:
        df = pd.read_sql(sql, r)
        df['measurement'] = df['measurement'].astype(str)
        # show all hide measurement selector when was only one measurement for all entities
        if len(df['measurement']) < 2:
            block_measurement = 'none'
        else:
            block_measurement = 'block'
    except (Exception,):
        df = ["No data"]
        block_measurement = 'none'
    return df['measurement'], block_measurement


def clean_filter(r):
    sql = "DROP TABLE IF EXISTS temp_table_ids"
    sql_drop = "DROP TABLE IF EXISTS temp_table_name_ids"

    r.execute(sql)
    r.execute(sql_drop)


def first_filter(query, query2, r):
    create_table = """ CREATE TEMP TABLE IF NOT EXISTS temp_table_name_ids as ({}) """.format(query)
    create_table_2 = """ CREATE TEMP TABLE IF NOT EXISTS temp_table_ids as ({}) """.format(query2)

    r.execute(create_table)
    r.execute(create_table_2)


def next_filter(query, query2, r):
    create_table = """ DELETE FROM temp_table_name_ids WHERE name_id NOT IN ({})""".format(query)
    create_table_2 = """ INSERT INTO temp_table_ids ({}) """.format(query2)

    r.execute(create_table)
    r.execute(create_table_2)


def add_categorical_filter(filters, n, r):
    subcategory = "$$" + "$$,$$".join(filters[1].get('sub')) + '$$'

    query = """SELECT DISTINCT ec.name_id FROM examination_categorical ec 
                WHERE ec.key = '{0}' AND ec.value IN ({1}) 
    """.format(filters[0].get('cat'), subcategory)
    query2 = """SELECT DISTINCT ec.name_id,ec.key FROM examination_categorical ec 
    WHERE ec.key = '{0}' AND ec.value IN ({1}) """.format(filters[0].get('cat'), subcategory,)

    if n == 1:
        first_filter(query, query2, r)
    else:
        next_filter(query, query2, r)


def add_numerical_filter(filters, n, r):
    from_to = filters[1].get('from_to').split(";")
    query = """ SELECT DISTINCT en.name_id FROM examination_numerical en 
    WHERE en.key = '{0}'  AND en.value BETWEEN {1} AND {2}""".format(filters[0].get('num'), from_to[0], from_to[1])
    query2 = """ SELECT DISTINCT en.name_id,en.key FROM examination_numerical en 
    WHERE key = '{0}' AND en.value BETWEEN {1} AND {2} """.format(filters[0].get('num'), from_to[0], from_to[1])

    if n == 1:
        first_filter(query, query2, r)
    else:
        next_filter(query, query2, r)


def create_temp_table_case_id(case_id, n, check_case_id, r):
    case_id_all = "$$" + "$$,$$".join(case_id) + "$$"

    query = """ SELECT DISTINCT name_id FROM patient WHERE case_id in ({0}) """.format(case_id_all)

    query2 = """ SELECT name_id,(CASE WHEN case_id !='' THEN 'case_id' END) as key 
    from patient where case_id in ({0}) """.format(case_id_all)
    if check_case_id == 'Yes' and n == 1:
        clean_filter(r)
    elif check_case_id == 'Yes' and n != 1:
        remove_one_filter('case_id', n, r)

    if n == 1:
        first_filter(query, query2, r)
    else:
        next_filter(query, query2, r)


def remove_one_filter(filters, filter_update, r):
    update_table = """ DELETE FROM temp_table_ids WHERE key = '{}' """.format(filters)
    sql_drop = "DROP TABLE IF EXISTS temp_table_name_ids"

    query = """ SELECT name_id FROM temp_table_ids 
                    GROUP BY name_id 
                    HAVING count(name_id) = {} """.format(filter_update)
    create_table = """ CREATE TEMP TABLE temp_table_name_ids as ({}) """.format(query)

    r.execute(update_table)
    r.execute(sql_drop)
    r.execute(create_table)


def checking_for_filters(date_filter, limit_filter, update_filter):
    if update_filter is None:
        filters = ''
    else:
        filters = """ inner join temp_table_name_ids as ttni on foo.name_id=ttni.name_id """

    if limit_filter.get('selected'):
        limit_selected = """ LIMIT {} OFFSET {} """.format(limit_filter.get('limit'), limit_filter.get('offset'))
    else:
        limit_selected = ''

    if date_filter[2] != 0:
        date_value1 = 'AND x."date" BETWEEN $${0}$$ AND $${1}$$ '.format(date_filter[0], date_filter[1])
        date_value2 = 'AND y."date" BETWEEN $${0}$$ AND $${1}$$'.format(date_filter[0], date_filter[1])
        date_value = 'AND "date" BETWEEN $${0}$$ AND $${1}$$'.format(date_filter[0], date_filter[1])
    else:
        date_value1 = ''
        date_value2 = ''
        date_value = ''

    return filters, limit_selected, date_value1, date_value2, date_value


def get_data(entities, what_table, measurement, limit, offset, sort, date_filter, update_filter, r):
    if sort[1] == 'desc':
        sort = desc(text(f'"{sort[0]}"'))
    else:
        sort = asc(text(f'"{sort[0]}"'))
    s = []
    for i, name in enumerate([TableCategorical, TableNumerical, TableDate]):
        if date_filter[2] != 0:
            values = name.date.between(date_filter[3], date_filter[4])
        else:
            values = text('')
        s.append(select(name.name_id, name.case_id, name.date, name.measurement, name.key,
                        name.value.cast(String).label('value')).
                 where(and_(name.key.in_(entities), name.measurement.in_(measurement), values)))
    s_union = union(s[0], s[1], s[2])

    if what_table == 'long':
        sql_statement, sql_statement_l = get_data_long_format(s_union, update_filter, limit, offset, sort)
    else:
        sql_statement, sql_statement_l = get_data_short_format(s_union, update_filter, entities, limit, offset, sort)

    try:
        df = pd.read_sql(sql_statement, r.connection())
        length = pd.read_sql(sql_statement_l, r.connection())
        length = length.iloc[0]['count']
        return df, length, None
    except (Exception,):
        df = pd.DataFrame()
        length = 0
        return df, length, "Problem with load data from database"


def get_data_long_format(s_union, update_filter, limit, offset, sort):
    sql_statement = select(s_union.c)
    sql_statement_l = select(func.count(s_union.c.name_id).label('count'))
    if update_filter != 0:
        sql_statement = sql_statement. \
            join(text('temp_table_name_ids'), s_union.c.name_id == text('temp_table_name_ids.name_id'))
        sql_statement_l = sql_statement_l. \
            join(text('temp_table_name_ids'), s_union.c.name_id == text('temp_table_name_ids.name_id'))
    sql_statement = sql_statement. \
        order_by(sort). \
        limit(limit).offset(offset)

    return sql_statement, sql_statement_l


def get_data_short_format(s_union, update_filter, entities, limit, offset, sort):
    s_group_by = select(s_union.c.name_id, s_union.c.case_id,  s_union.c.date, s_union.c.measurement, s_union.c.key,
                        func.string_agg(s_union.c.value, literal_column("';'")).label('value')). \
        group_by(s_union.c.name_id, s_union.c.case_id, s_union.c.date, s_union.c.measurement, s_union.c.key)

    case_when = ""
    for i in entities:
        case_when += """ min(CASE WHEN key = $${0}$$ then value end) as "{0}",""".format(i)
    case_when = case_when[:-1]
    sql_statement = select(s_group_by.c.name_id, s_group_by.c.case_id, s_group_by.c.date, s_group_by.c.measurement,
                           text(case_when))

    if update_filter != 0:
        sql_statement = sql_statement.\
            join(text('temp_table_name_ids'), s_group_by.c.name_id == text('temp_table_name_ids.name_id'))
    sql_statement = sql_statement.\
        group_by(s_group_by.c.name_id, s_group_by.c.case_id, s_group_by.c.date, s_group_by.c.measurement)
    sql_statement_l = select(func.count(sql_statement.c.name_id).label('count'))
    sql_statement = sql_statement.\
        order_by(sort). \
        limit(limit).offset(offset)
    return sql_statement, sql_statement_l


def get_basic_stats(entity, measurement, date_filter, limit_filter, update_filter, r):
    n = select(func.count(distinct(Patient.name_id)).label('count'))
    s22 = []

    if date_filter[2] != 0:
        values = TableNumerical.date.between(date_filter[3], date_filter[4])
    else:
        values = text('')

    if limit_filter.get('selected') is not None:
        for e in entity:
            s2 = select(TableNumerical.key, TableNumerical.measurement, TableNumerical.name_id,
                        func.avg(TableNumerical.value).label('value'))
            if update_filter['filter_update'] != 0:
                j = join(TableNumerical, text("temp_table_name_ids"),
                         TableNumerical.name_id == text("temp_table_name_ids.name_id"))
                s2 = s2.select_from(j)
            s22.append(s2.where(and_(TableNumerical.key == e, TableNumerical.measurement.in_(measurement), values)).
                       group_by(TableNumerical.name_id, TableNumerical.key, TableNumerical.measurement).
                       limit(limit_filter.get('limit')).offset(limit_filter.get('offset')))
        sql_part2 = union(*s22)

    else:
        sql_part2 = select(TableNumerical.name_id, TableNumerical.key, TableNumerical.measurement,
                           func.avg(TableNumerical.value).label('value'))
        if update_filter['filter_update'] != 0:
            j = join(TableNumerical, text("temp_table_name_ids"),
                     TableNumerical.name_id == text("temp_table_name_ids.name_id"))
            sql_part2 = sql_part2.select_from(j)

        sql_part2 = sql_part2.where(and_(TableNumerical.key.in_(entity), TableNumerical.measurement.in_(measurement),
                                         values)).\
            group_by(TableNumerical.name_id, TableNumerical.key, TableNumerical.measurement)

    sql_part2 = sql_part2.cte('distinct_query')
    sql = select(sql_part2.c.key, sql_part2.c.measurement,
                 func.count(sql_part2.c.name_id).label('count'), func.min(sql_part2.c.value).label('min'),
                 func.max(sql_part2.c.value).label('max'),
                 func.avg(sql_part2.c.value).label('mean'),
                 func.stddev(sql_part2.c.value).label('stddev'),
                 label('stderr', func.stddev(sql_part2.c.value).label('stddev')/func.sqrt(func.count(sql_part2.c.value))
                       ),
                 func.percentile_cont(0.5).within_group(sql_part2.c.value).label('median')).\
        group_by(sql_part2.c.key, sql_part2.c.measurement).\
        order_by(sql_part2.c.key, sql_part2.c.measurement)

    try:
        df = pd.read_sql(sql, r.connection())
        n = pd.read_sql(n, r.connection())
        n = n['count']
        df['count NaN'] = int(n) - df['count']
        df = df.round(2)

        return df, None
    except (Exception,):
        return None, "Problem with load data from database"


def get_cat_date_basic_stats(entity, measurement, date_filter, limit_filter, update_filter, table, r):
    if table == 'examination_categorical':
        name = TableCategorical
    else:
        name = TableDate
    n = select(func.count(distinct(Patient.name_id)).label('count'))
    s22 = []

    if date_filter[2] != 0:
        values = name.date.between(date_filter[3], date_filter[4])
    else:
        values = text('')

    if limit_filter.get('selected') is not None:
        for e in entity:
            s2 = select(name.key, name.measurement, name.name_id)
            if update_filter['filter_update'] != 0:
                j = join(name, text("temp_table_name_ids"),
                         name.name_id == text("temp_table_name_ids.name_id"))
                s2 = s2.select_from(j)
            s22.append(s2.where(and_(name.key == e, name.measurement.in_(measurement), values)).
                       group_by(name.name_id, name.key, name.measurement).
                       limit(limit_filter.get('limit')).offset(limit_filter.get('offset')))
        sql_part2 = union(*s22)
    else:
        sql_part2 = select(name.name_id, name.key, name.measurement)
        if update_filter['filter_update'] != 0:
            j = join(name, text("temp_table_name_ids"),
                     name.name_id == text("temp_table_name_ids.name_id"))
            sql_part2 = sql_part2.select_from(j)

        sql_part2 = sql_part2.where(and_(name.key.in_(entity), name.measurement.in_(measurement),
                                         values)). \
            group_by(name.name_id, name.key, name.measurement)

    sql_part2 = sql_part2.cte('distinct_query')

    sql = select(sql_part2.c.key, sql_part2.c.measurement, func.count(sql_part2.c.name_id).label('count')).\
        group_by(sql_part2.c.key, sql_part2.c.measurement).\
        order_by(sql_part2.c.key, sql_part2.c.measurement)

    try:
        n = pd.read_sql(n, r.connection())
        n = n['count']
        df = pd.read_sql(sql, r.connection())
        df['count NaN'] = int(n) - df['count']
        return df, None
    except (Exception,):
        return None, "Problem with load data from database"


def get_scatter_plot(add_group_by, axis, measurement, categorical_entities, date_filter, limit_filter, update_filter,
                     r):

    if date_filter[2] != 0:
        values = TableNumerical.date.between(date_filter[3], date_filter[4])
    else:
        values = text('')

    adalias2 = aliased(TableNumerical)

    if not add_group_by:
        sql = select(TableNumerical.name_id, func.avg(TableNumerical.value).label(f'{axis[0]}_{measurement[0]}'),
                     func.avg(adalias2.value).label(f'{axis[1]}_{measurement[1]}'))
        if update_filter['filter_update'] != 0:
            j = join(TableNumerical, text("temp_table_name_ids"),
                     TableNumerical.name_id == text("temp_table_name_ids.name_id"))
            sql = sql.select_from(j)
        sql = sql.where(and_(TableNumerical.key == axis[0], TableNumerical.measurement == measurement[0],
                             adalias2.key == axis[1], adalias2.measurement == measurement[1],
                             TableNumerical.name_id == adalias2.name_id, values)). \
            group_by(TableNumerical.name_id)
    else:
        subquery = select(TableNumerical.name_id, TableNumerical.value.label('value1'), adalias2.value.label('value2'))
        if update_filter['filter_update'] != 0:
            j = join(TableNumerical, text("temp_table_name_ids"),
                     TableNumerical.name_id == text("temp_table_name_ids.name_id"))
            subquery = subquery.select_from(j)
        subquery = subquery.where(and_(TableNumerical.key == axis[0], TableNumerical.measurement == measurement[0],
                                       adalias2.key == axis[1], adalias2.measurement == measurement[1]),
                                  TableNumerical.name_id == adalias2.name_id, values)

        sql = select(subquery.c.name_id, func.avg(subquery.c.value1).label(f'{axis[0]}_{measurement[0]}'),
                     func.avg(subquery.c.value2).label(f'{axis[1]}_{measurement[1]}'),
                     func.string_agg(distinct(TableCategorical.value),
                                     literal_column("'<br>'")).label(categorical_entities[0])).\
            join(TableCategorical, TableCategorical.name_id == subquery.c.name_id).\
            where(and_(TableCategorical.key == categorical_entities[0],
                       TableCategorical.value.in_(categorical_entities[1]))).\
            group_by(subquery.c.name_id)

    if limit_filter.get('selected') is not None:
        sql = sql.limit(limit_filter.get('limit')).offset(limit_filter.get('offset'))

    try:
        df = pd.read_sql(sql, r.connection())
        if df.empty:
            df, error = df, "One of the selected entities is empty"
            return df, error
        else:
            return df, None
    except (Exception,):
        return None, "Problem with load data from database"


def get_bar_chart(categorical_entities, measurement, date_filter, limit_filter, update_filter, r):

    if date_filter[2] != 0:
        values = TableCategorical.date.between(date_filter[3], date_filter[4])
    else:
        values = text('')

    subquery = select(func.string_agg(distinct(TableCategorical.value), literal_column("'<br>'")).label('value'),
                      TableCategorical.measurement)
    if update_filter['filter_update'] != 0:
        j = join(TableCategorical, text("temp_table_name_ids"),
                 TableCategorical.name_id == text("temp_table_name_ids.name_id"))
        subquery = subquery.select_from(j)
    subquery = subquery.where(and_(TableCategorical.key == categorical_entities[0],
                                   TableCategorical.value.in_(categorical_entities[1]),
                                   TableCategorical.measurement.in_(measurement), values)).\
        group_by(TableCategorical.name_id, TableCategorical.measurement)

    if limit_filter.get('selected') is not None:
        subquery = subquery.limit(limit_filter.get('limit')).offset(limit_filter.get('offset'))

    sql = select(subquery.c.value.label(categorical_entities[0]), subquery.c.measurement,
                 func.count(subquery.c.value).label('count')).group_by(subquery.c.value, subquery.c.measurement)

    try:
        df = pd.read_sql(sql, r.connection())
        if df.empty:
            return df, "The entity wasn't measured"
        else:
            df.columns = [categorical_entities[0], 'measurement', 'count']
            df[categorical_entities[0]] = df[categorical_entities[0]].str.wrap(30).replace(to_replace=[r"\\n", "\n"],
                                                                                           value=["<br>", "<br>"],
                                                                                           regex=True)
            return df, None
    except (Exception,):
        return None, "Problem with load data from database"


def get_histogram_box_plot(entities, measurement, date_filter, limit_filter, update_filter, r):

    if date_filter[2] != 0:
        date_group_by = TableNumerical.date.between(date_filter[3], date_filter[4])
    else:
        date_group_by = text('')

    sql2 = select(TableNumerical.name_id, TableNumerical.measurement, func.avg(TableNumerical.value).label(entities[0]),
                  TableCategorical.value.label(entities[1]))

    if update_filter['filter_update'] != 0:
        j = join(TableNumerical, text("temp_table_name_ids"),
                 TableNumerical.name_id == text("temp_table_name_ids.name_id"))
        sql2 = sql2.select_from(j)
    sql2 = sql2.where(and_(TableNumerical.key == entities[0], TableCategorical.key == entities[1],
                           TableCategorical.value.in_(entities[2]), TableNumerical.measurement.in_(measurement),
                           date_group_by,
                           TableCategorical.name_id == TableNumerical.name_id))
    sql2 = sql2.group_by(TableNumerical.name_id, TableNumerical.measurement, TableCategorical.value)

    if limit_filter['selected'] == 'true':
        sql2 = sql2.limit(limit_filter['limit']).offset(limit_filter['offset'])

    try:
        df = pd.read_sql(sql2, r.connection())
        if df.empty or len(df) == 0:
            return df, "The entity {0} or {1} wasn't measured".format(entities[0], entities[1])
        else:
            df.columns = ["name", 'measurement', entities[0], entities[1]]
            df[entities[1]] = df[entities[1]].str.wrap(30).replace(to_replace=[r"\\n", "\n"], value=["<br>", "<br>"],
                                                                   regex=True)
            return df, None
    except (Exception,):
        return None, "Problem with load data from database"


def get_heat_map(entities, date_filter, limit_filter, filters, r):
    case_when = ""
    for i in entities:
        case_when += """ min(CASE WHEN key = $${0}$$ then value end) as "{0}",""".format(i)
    case_when = case_when[:-1]

    sql2 = select(TableNumerical.name_id, text(case_when))

    if filters['filter_update'] != 0:
        j = join(TableNumerical, text("temp_table_name_ids"),
                 TableNumerical.name_id == text("temp_table_name_ids.name_id"))
        sql2 = sql2.select_from(j)

    if date_filter[2] != 0:
        sql2 = sql2.where(TableNumerical.date.between(date_filter[3], date_filter[4]))

    sql2 = sql2.group_by(TableNumerical.name_id)

    if limit_filter.get('selected') is not None:
        sql2 = sql2.limit(limit_filter['limit']).offset(limit_filter['offset'])

    try:
        df = pd.read_sql(sql2, r.connection())

        if df.empty:
            return df, "The entity wasn't measured"
        else:
            return df, None
    except (Exception,):
        return None, "Problem with load data from database"
