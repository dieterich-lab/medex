# Create a new page 
To create a new page the following steps have to be done:

1. Add a link in the main menu
    
    1.1. In the file `templates/layout.html` find a div container `<div class="navbar">` 
    
    1.2. and add inside of it a new link. For example:
`<a class="nav-link" href="/new_page">New Page</a>` 

2. Create a url_handler (a view function)
    
    2.1. In the directory `url_handlers` add a file `new_page.py`
    
    2.2. In this file create a blueprint: 

```
new_page = Blueprint('new_page', __name__, 
template_folder='new_page_templates')
```
.

2.3. Register blueprint in the main app file (`webserver.py`)
`app.register_blueprint(new_page)`

3. Create a template. 

    3.1. For all pages there is a meta-template `layout.html`. So each template is inherited from this file. Example of usage:

    ```
    {% extends "layout.html" %}
    {% block body %}
    here is to write html
    {% endblock %}
    ```

    3.2. Separate files. Sometimes it makes sense to separate the html structure into a few files. For example, the page `basic_stats` has a tab view, so each tab is in a single file. Both tabs are included in the main file `templates/basic_stats/basic_stats.html`. Example:

    ```
    {% include 'basic_stats/categorical_tab.html' %}
    {% include 'basic_stats/numeric_tab.html' %}
    ```