=============
Tethys Gizmos
=============

Gizmos are building blocks that can be used to create beautiful interactive controls for web apps. Using gizmos,
developers can add date-pickers, plots, and maps to their templates with minimal coding.

Installation
------------

Tethys Gizmos can be installed via pip or by downloading the source. To install via pip or easy_install::

    pip install django-tethys_gizmos

To install via download::

    git clone https://github.com/CI-WATER/django-tethys_gizmos.git
    cd django-tethys_gizmos
    python setup.py install

Django Configuration
--------------------

1. Add "tethys_gizmos" to your INSTALLED_APPS setting like this::

    INSTALLED_APPS = (
        ...
        'tethys_gizmos',
    )

2. Add the context processor to settings. For example::

    TEMPLATE_CONTEXT_PROCESSORS = ('django.contrib.auth.context_processors.auth',
                                   'django.core.context_processors.debug',
                                   'django.core.context_processors.i18n',
                                   'django.core.context_processors.media',
                                   'django.core.context_processors.static',
                                   'django.core.context_processors.tz',
                                   'tethys_gizmos.context_processors.tethys_gizmos_context')

3. Include the Tethys Gizmos URLconf to your project urls.py with the "gizmos" namespace::

    url(r'^gizmos/', include('tethys_gizmos.urls', namespace='gizmos'))

4. Tethys Gizmos makes extensive use of Twitter Bootstrap and Jquery. These libraries must be included in all templates
that use gizmos. Because of the prevalent use of these two libraries, we leave it to the developer to decide how to
provide these dependencies. It is suggested that you include them in your "page.html" (see below) or some other base
template that all pages in your website use.


5. Tethys Gizmos includes a showcase of all the available gizmos including live demos and code examples. To get this page
working you will need to create a template called "page.html" in your base "templates" directory that includes blocks
called "styles", "bodytag", "primary_content", and "scripts". Also include the Bootstrap and Jquery dependencies. Your
"page.html" should look something like this::


    <!DOCTYPE html>
    <html>
        <head>
            <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.2.0/css/bootstrap.min.css">
            <script src="https://code.jquery.com/jquery-2.1.1.min.js"></script>
            <script src="https://maxcdn.bootstrapcdn.com/bootstrap/3.2.0/js/bootstrap.min.js"></script>
            {% block styles %}
            {% endblock %}
        </head>
        <body {% block bodytag %}{% endblock %}>
            {% block primary_content %}
            {% endblock %}

            {% block scripts %}
            {% endblock %}
        </body>
    </html>


.. note:: The gizmos work best if your Jquery and Bootstrap JavaScript scripts are included in the head of your document as is depicted above.


Quick Start
-----------

What does "minimal coding" mean? Take a look at the following example. Let's say you want to include a date
picker in your template using a gizmo. First, create a dictionary with all the configuration options
for the date picker (more on that later) in your view/controller for the template and add it to the context::

    def my_view(request):
        date_picker_options = {'display_text': 'Date',
                         'name': 'date1',
                         'autoclose': True,
                         'format': 'MM d, yyyy',
                         'start_date': '2/15/2014',
                         'start_view': 'decade',
                         'today_button': True,
                         'initial': 'February 15, 2014'}
        
        context = {'date_picker_options': date_picker_options}
        
        return render(request, 'path/to/my/template.html', context)


Next, open the template you intend to add the gizmo to and load the **tethys_gizmos** library. Be sure to
do this somewhere near *the top* of your template--before any gizmo occurrences. This only needs to be
done once for each template that uses gizmos::

    {% load tethys_gizmos %}


Now, use the **gizmo** tag to insert the date picker anywhere in your template. Pass the name of the gizmo
and the options dictionary that you passed to the template from your view as arguments::

    {% gizmo date_picker date_picker_options %}

Finally, *at the end* of your template--after all of the **gizmo** tags--insert the **gizmo_dependencies**
tag. This only needs to be done once for each template that uses gizmos.

::
    
    {% gizmo_dependencies %}

.. note:: When using Tethys Gizmos in Tethys App development, it is not necessary to include the **gizmo_dependencies** tag in the template. The dependencies are already included in the **app_base** template.

All together your template may look something like this::

  {% load tethys_gizmos %}
  <DOCTYPE html>
  <html>
    <head>
      ...
    </head>
    <body>
      ...
      {% gizmo date_picker date_picker_options %}
      ...
      {% gizmo_dependencies %}
    </body>
  </html>

How it Works
------------

Gizmos are composed of HTML, JavaScript, and CSS. When the template is rendered, each of the **gizmo**
tags are replaced by the HTML that is needed to render the gizmo. All gizmos accept a Python dictionary
with options for configuring the gizmo. The options for each gizmo are documented on this page.

The JavaScript and CSS dependencies are loaded into the template at the location of the **gizmo_dependencies**
tag. Note that the **gizmo_dependencies** tag must be called *after* all of the **gizmo** tags
otherwise some of the dependencies may not be loaded properly.

Optionally, the **gizmo_dependencies** tag can be called with either **js** or **css** to load only
the JavaScript or only the CSS dependencies, respectively. The rule that this tag must be called after all
**gizmo** tags still applies. The **gizmo_dependencies** *must* be called twice (once for each option)
when this feature is used.

::

    {% gizmo_dependencies js %}
    {% gizmo_dependencies css %}


The **tethys_gizmos** library must be loaded at the top of the template to provide the **gizmo** and
**gizmo_dependencies** template tags.

