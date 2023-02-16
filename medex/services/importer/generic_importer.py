from abc import abstractmethod
from typing import TextIO, List, Dict

from flask_sqlalchemy.session import Session
from sqlalchemy import insert

from modules.models import Base


class HeaderLineMissing(Exception):
    pass


class BadHeaderLine(Exception):
    pass


class GenericImporter:
    """
    The GenericImporter is an abstract base class for importers, which
    read data from a file and write them to one or more database tables.
    It buffers the data read to do bulk inserts once sufficient data has
    been collected for one table.

    The first line of the input data must contain a header listing the columns
    in the order they appear in the remaining file. After that empty lines are
    silently ignored. The input data must have one record per line. Columns are
    separated by a comma (','). White space at the beginning and the end of any
    data item is ignored.
    """

    class _Buffer:
        MAX_BUFFER_ITEMS = 100

        def __init__(self, table: Base, db_session: Session):
            self._table = table
            self._db_session = db_session
            self._items = []

        def add_item(self, item: Dict[str, any]):
            self._items.append(item)
            if len(self._items) >= self.MAX_BUFFER_ITEMS:
                self.flush()

        def flush(self):
            if len(self._items) == 0:
                return
            self._db_session.execute(
                insert(self._table), self._items
            )
            self._items = []

    def __init__(
            self,
            file_handle: TextIO,
            source_name: str,
            known_columns: List[str],
            required_columns: List[str],
            db_session: Session
    ):
        """
        The constructor of the GenericImporter requires a file-like object 'file_handle'
        to read the data from. The parameter 'source_name' should describe, where the
        data comes from, e.g. a file name. It is used in error messages and warnings.

        A list of known column 'column_list' is supplied to define, which
        data fields can be processed. If a name not included in the list is found
        in the header, a warning is generated and that column is ignored in the input
        data. Another list of 'required_columns' indicates a minimal set of columns,
        which must be declared in the header. If one is missing a BadHeaderLine exception
        will be raised when the file is processed. A database session 'db_session' is
        needed to store the data.
        """
        self._file_handle = file_handle
        self._source_name = source_name
        self._known_columns = known_columns
        self._required_columns = required_columns
        self._db_session = db_session

        self._column_list = None
        self._line_number = None
        self._buffer_by_table_name: Dict[str, GenericImporter._Buffer] = {}

    @abstractmethod
    def parse_row(self, values: Dict[str, str]) -> (Dict[str, any], Base):
        """
        Validates the given values gives as dict, which maps the column name to the
        string found in the input file. It returns tuple of:
        1) A dict mapping the column names to the values converted to the type needed
        2) A SqlAlchemy table object the data should be written to.
        In case of an error raise a ValueError(message). The message should describe
        what is wrong with the record. The file name and line number will be
        automatically added. The record will be skipped during the import.
        """
        pass

    def import_all(self):
        self._line_number = 1
        self._process_header()
        for line in self._file_handle:
            self._line_number += 1
            self._process_line(line)
            if self._line_number % 1000 == 0:
                print(f"   ... at line {self._line_number} ...")
        self._finish()

    def _process_header(self):
        try:
            line = next(self._file_handle)
        except StopIteration:
            raise HeaderLineMissing(f"The header line is missing in {self._source_name}.")
        self._column_list = [x.strip() for x in line.split(',')]
        self._check_for_unknown_columns()
        self._check_for_required_columns()

    def _check_for_unknown_columns(self):
        for column in self._column_list:
            if column not in self._known_columns:
                print(
                    f"Warning: Header of {self._source_name} does contain unknown column '{column}' - will be ignored."
                )

    def _check_for_required_columns(self):
        for column in self._required_columns:
            if column not in self._column_list:
                raise BadHeaderLine(
                    f"The header line in {self._source_name} does not contain the required column '{column}'."
                )

    def _process_line(self, line):
        if line.strip() == '':
            return
        values = [x.strip() for x in line.split(',')]
        try:
            raw_values = self._map_values(values)
            cooked_values, table = self.parse_row(raw_values)
            self.buffer_values_for_bulk_insert(cooked_values, table)
        except ValueError as e:
            print(f"Warning: Failed to parse {self._source_name}, line {self._line_number}: {str(e)} - skipping.")

    def _finish(self):
        self._file_handle.close()
        for buffer in self._buffer_by_table_name.values():
            buffer.flush()
        self._db_session.commit()

    def buffer_values_for_bulk_insert(self, cooked_values, table):
        if table.__tablename__ not in self._buffer_by_table_name:
            self._buffer_by_table_name[table.__tablename__] = GenericImporter._Buffer(
                db_session=self._db_session,
                table=table
            )
        buffer = self._buffer_by_table_name[table.__tablename__]
        buffer.add_item(cooked_values)

    def _map_values(self, values):
        values_count = len(values)
        column_count = len(self._column_list)
        if values_count != column_count:
            raise ValueError(f"The number of the columns ({values_count}) is not {column_count}")
        return {
            self._column_list[i]: values[i]
            for i in range(column_count)
        }
