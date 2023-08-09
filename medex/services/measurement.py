from typing import Optional

from sqlalchemy import select, union, func
from sqlalchemy.orm import Session

from medex.database_schema import HeaderTable, NumericalValueTable, CategoricalValueTable, DateValueTable
from medex.dto.measurement import MeasurementInfo


class MeasurementService:
    def __init__(self, db_session: Session):
        self._db_session = db_session
        self._cache: Optional[MeasurementInfo] = None

    def get_info(self) -> MeasurementInfo:
        if self._cache is None:
            self._cache = MeasurementInfo(
                display_name=self._get_display_name(),
                values=self._get_measurements_sorted_by_first_appearance(),
            )
        return self._cache.copy(deep=True)

    def _get_display_name(self):
        rs = self._db_session.execute(
            select(HeaderTable.measurement)
        )
        return rs.first().measurement

    def _get_measurements_sorted_by_first_appearance(self):
        list_query_tables = [
            select(table.measurement, table.date_time)
            for table in [CategoricalValueTable, NumericalValueTable, DateValueTable]
        ]
        query_union = union(*list_query_tables).subquery()
        measurement_col = query_union.exported_columns.measurement
        first_date_col = func.min(query_union.exported_columns.date_time).label('first_date)')
        statement = (
            select(measurement_col, first_date_col)
            .group_by(measurement_col)
            .order_by(first_date_col.asc())
        )
        rs = self._db_session.execute(statement).all()
        return [x.measurement for x in rs]
