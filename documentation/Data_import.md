# Data Import

## Data Format

### General Structure

The data for the input is supplied in these files:

* **entities.csv:** List of types of data that have to be loaded. The data needs to contain at least a
  key to identify the entity and a type which may be 'String' for categorical data, 'Double' for numerical
  data or 'Date' for dates.
* **dataset.csv:** List of data items, which must contain at least a 'name_id' to identify
  the patient, a 'key' referring to an entity defined in the above file and a 'value'
  in a format matching the entity.

Each of the files starts with a header line followed by data records, one record per line
in UTF-8 encoding. The header line defines the order of the data fields. The data fields
in each record are separated by ','. Unknown columns are skipped during data import.
Leading and trailing white space is ignored. Also empty lines are ignored.

Examples for both files can befound in the examples folder.

### Paths

The data is expected in path, which is mapped to /app/import inside the Docker
container. In case of a successful import the file `__IMPORT_MARKER__` is created in this directory.

### entities.csv

The `entities.csv` file may contain the following fields:

* key (required)
* type (required, 'String', 'Double' or 'Date')
* synonym (optional, unused so far)
* description (optional)
* unit (optional, unused so far)
* show (optional, unused - should be '+' to mark entities show by default in table browser)

### dataset.csv

The `dataset.csv` may contain these fields:

* name_id (required, identifies the patient)
* case_id (required, but unused?)
* measurement (optional, a string which identifies the visit or examination the data was collected at, e.g. 'baseline', '1 year follow up')
* date (optional, format YYYY-MM-DD)
* time (optional, format HH:MM:SS)
* key (required, identifies the entity)
* value (required, string for categorical entities, number for numerical, date in fromat YYYY-MM-DD for date)

## Triggering Import

An import will be done on start up in following cases:

* The file `__IMPORT_MARKER__` is not present in the import directory.
* The entities.csv or dataset.csv is newer than `__IMPORT_MARKER__`.
* The database revision can not be determined because the table alembic_version is not present.

Prior to the import the database will be reset by dropping all tables but alembic_version.

To force an import, just remove the file `__IMPORT_MARKER__`.
