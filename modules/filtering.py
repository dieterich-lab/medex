from sqlalchemy import text


def checking_date_filter(date_filter, table):
    if date_filter[2] != 0:
        values = table.date.between(date_filter[3], date_filter[4])
    else:
        values = text('')

    return values


def apply_limit_to_sql_query(limit_filter, sql):
    if limit_filter.get('selected') is not None:
        sql = sql.limit(limit_filter['limit']).offset(limit_filter['offset'])
    else:
        sql = sql
    return sql
