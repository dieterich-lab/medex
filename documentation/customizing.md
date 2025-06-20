# Customizing MedEx

Since version 1.1 it is possible to do minimal customizing for MedEx.
To do so, add a line mapping to your docker-compose.yml file that maps
a folder of your choice (e.g. /you/custom/data) to the folder
/app/medex/controller/root/resources/custom inside the container

```
services:
  medex:
    ...
    volumes:
      ...
      /you/custom/data:/app/medex/controller/root/resources/custom
```

Your local folder may contain any of the following files to overwrite
the defaults:

* **favicon.ico:** Icon used by the browser to represent the web page.
* **message_catalog.json:** Use to replace the terms useed in app. Set
  headline_title to a value different to 'None' to add a headline
  to the application.
* **app_config.json:** This file contains various feature switches.
  Use them to switch off menu items, which make no sense for 
  your data load.

As starting point the default settings can be used, which can be found
in this repository in the folder medex/controller/root/resources.
