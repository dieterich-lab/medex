from typing import Optional, TextIO

from sqlalchemy import insert
from sqlalchemy.orm import Session

from medex.database_schema import HeaderTable


class HeaderImporter:
    DEFAULT_HEADERS = ['Patient_ID', 'Case_ID', 'Measurement']

    def __init__(self, file_handle: Optional[TextIO], source_name: Optional[str], db_session: Session):
        self._file_handle = file_handle
        self._source_name = '(unknown)' if source_name is None else source_name
        self._db_session = db_session

    def setup_header_names(self):
        headers = self._get_headers()
        self._store_headers(headers)

    def _get_headers(self):
        if self._file_handle is None:
            print('No header input file - using default header names.')
            return self.DEFAULT_HEADERS
        line = self._file_handle.readline()
        self._file_handle.close()
        headers = [x.strip() for x in line.split(',')]
        count = len(headers)
        if count != 3:
            print(f"WARNING: The file with the headers {self._source_name} must contain 3 headers separated by ','.")
            print('WARNING: Continuing with default header names.')
            return self.DEFAULT_HEADERS
        return headers

    def _store_headers(self, headers):
        # Why don't we have a field case_id in the header table to store headers[1]?
        # Unknown so far ...
        self._db_session.execute(
            insert(HeaderTable).values(patient_id=headers[0], measurement=headers[2])
        )
        self._db_session.commit()
