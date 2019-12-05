Research Data Warehouse
=======================

Project Structure
-----------------
This is a short description of the project structure

The project contains the following directories:
1. `data_warehouse`
2. `documentation`
3. `flaskr`
(and a couple of more)


`flaskr`
--------

This is the main directory of the app. It contains `hello.py` file (todo: rename it!) which is the main app file. Set environmental variable `FLASK_APP` to refer to this file in order to run the project (described in quickstart section).
This file *should NOT* contain the view functions (or url_handlers - depends on the terminology you use).
Each url has to be handled in a separate file as a Blueprint (for details check http://flask.pocoo.org/docs/1.0/blueprints/), and should be in the directory `url_handlers`.
As the project has a lot of urls, it makes the code totaly unreadable when everything is handled in one file. So please do a favor to yourself and to the future developers of the project and DO separate the code.

`flaskr/static`

Contains static files, e.g. external js libraries, or css, which are not developed by us, but downloaded as external resources. The directory static/js contains the js files which are created **BY US**.

`flask/templates`
Contains html templates which will be rendered by related view. For big pages (like `statistics` page) it is recommended to separate the logic into multiple files instead of writing everything in one file.

`flask/url_handlers`
As mentioned above, this directory contains url hanlders, one file is one url. These files have to be registered in the hello.py as Blueprints


`data_warehouse`
----------------

The directory contains standalone scripts, which describe some util functions e.g. to set up the database, to import the dataset, etc.


`documentation`
---------------
The directory contains documentation files related to the project.
This is documentation for the developers, not for the end users. Therefor, all the technical details regarding implementation should be documented here. Each file contains a small piece of information. It is again *STRONGLY* recommended to separate the documentation into multiple files and do not use one for everything.

