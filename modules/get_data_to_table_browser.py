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
