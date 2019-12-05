# HTML and Javascript
For any javascript dependencies it is highly recommended not to use external urls, but to download libraries and store them in the `static` directory. Sometimes external links can break, or be moved to another address, or there is a restricted internet connection. To avoid all these problems, we just download the files and keep them locally in the `static` directory.
To use these libraries in a template, put it in the normal `<script>` tag (for js files) or `<link>` tag (for css files), where the src should be assigned via a function `static_url`. Example:
`<script src="{{ static_url('static', filename='my_js_library.js') }}">`

## Structure
When it is necessary to implement some js on a web-page, for this web-page create a separate js file in the directory `static/js`. The name of js file is the same as the template name. Small files are better readable, cause it's clear what comes from where, and it is easier to debug! So do not put all the js in one file.

## Form Controls
For creating elements on the page, I use `bootstrap` library. Bootstrap has all the components, like buttons, inputs, tables and so on, with pre-defined styles, as well as the layout system, and many interesting controls with already implemented callbacks. And many other usefull things. More details can be found here: https://getbootstrap.com/docs/4.0/components/forms/
It has some dependencies (e.g. jquery), which are added to the `layout.html` file and are stored locally in the `static` directory.

## Plots
For plots there is a library `highcharts.js`.  More details: https://www.highcharts.com/docs
