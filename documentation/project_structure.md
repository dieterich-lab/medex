Research Data Warehouse
=======================

Project Structure
-----------------
This is a description of the project structure

The project contains the following directories:
1. `medex`
2. `dataset_example`
3. `documentation`
4. `import`
5. `modules`
6. `scripts`
7. `serverside`
8. `static`
9. `templates`
10. `url_handlers`


medex
--------

This is the main directory of the app. It contains `webserver.py` file which is the main app file.
This file *should NOT* contain the view functions (or url_handlers - depends on the terminology you use).
Each url has to be handled in a separate file as a Blueprint (for details check http://flask.pocoo.org/docs/1.0/blueprints/), and should be in the directory `url_handlers`.
As the project has a lot of urls, it makes the code totally unreadable when everything is handled in one file. So please do a favor to yourself and to the future developers of the project and DO separate the code.

The directory contains also `docker-compose.yml` and `Dockerfile` for building docker image for application. The `docker-compose.yml` is a tool for
defining and running multi-container Docker application, more details https://docs.docker.com/compose/. In our case docker application consists container for database
and for web frontend. Docker build image by reading the instructions from a `Dockerfile`, more details https://docs.docker.com/engine/reference/builder/.

Pipfile specify packages requirements for our application. This file contain all necessary libraries for application working. If we need some new library for working
application pipfile need to be update accordingly.

`medex/static`
--------------
Contains static files, e.g. external js libraries, or css, which are not developed by us, but downloaded as external resources. The directory static/js contains the js files which are created **BY US**.

`medex/templates`
-----------------
Contains html templates which will be rendered by related view. For big pages (like `statistics` page) it is recommended to separate the logic into multiple files instead of writing everything in one file.

`medex/url_handlers`
--------------------
As mentioned above, this directory contains url handlers, one file is one url. These files have to be registered in the webserver.py as Blueprints

more about `static`, `templates` and `url_handlers` in [html_and_js.md](https://github.com/dieterich-lab/medex/blob/PostgreSQL/documentation/html_and_js.md) and [creating_a_new_page.md](https://github.com/dieterich-lab/medex/blob/PostgreSQL/documentation/creating_a_new_page.md).

`medex/serverside`
--------------
This directory, as the name suggests, contains the code to display the table in the browser using the server-side option.

`medex/scripts`
---------------

This directory contain start.sh file (Bourne shell script).The start.sh file contain commands which export database environmental variables and flask environmental variables  
 and command for running flask application.  


`medex/modules`
----------------
 This directory contains files for create database and import data from database to application,
  more about files and data import in [Data_import.md](https://github.com/dieterich-lab/medex/blob/PostgreSQL/documentation/Data_import.md)


`medex/import`
----------------

In this folder there should be files looking like example files in `dataset_examples` directory we want to load into the application.

`medex/dataset_examples`
------------------------

The directory contains example files. The files with data to import to application should look like example file. 

`medex/documentation`
----------------------

The directory contains documentation files related to the project.
This is documentation for the developers, not for the end users. Therefor, all the technical details regarding implementation should be documented here. Each file contains a small piece of information. It is again *STRONGLY* recommended to separate the documentation into multiple files and do not use one for everything.

