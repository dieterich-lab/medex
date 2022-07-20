from modules.models import TableNumerical, TableCategorical
from sqlalchemy.sql import select
from sqlalchemy import and_, func
import pandas as pd
from modules.filtering import checking_filter, checking_date_filter


def get_histogram_box_plot(entities, measurement, date_filter, limit_filter, update_filter, r):
    values = checking_date_filter(date_filter, TableNumerical)
    sql2 = select(TableNumerical.name_id, TableNumerical.measurement, func.avg(TableNumerical.value).label(entities[0]),
                  TableCategorical.value.label(entities[1]))
    sql2 = checking_filter(update_filter, TableNumerical, sql2)
    sql2 = sql2.where(and_(TableNumerical.key == entities[0], TableCategorical.key == entities[1],
                           TableCategorical.value.in_(entities[2]), TableNumerical.measurement.in_(measurement),
                           values,
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
