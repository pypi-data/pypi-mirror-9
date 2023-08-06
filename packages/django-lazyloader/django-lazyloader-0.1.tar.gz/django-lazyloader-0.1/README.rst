=====
Django-Lazyloader
=====

Django-Lazyloader is a simple Django app which helps displaying Django objects as either HTML or JSON.

Quick start
-----------

1.  Add "lazyloader" to your INSTALLED_APPS setting like this::

        INSTALLED_APPS = (
            ...
            'lazyloader',
        )

2.  Include the lazyloader URLconf in your project urls.py like this::

        url(r'^lazyloader/', include('lazyloader.urls')),

3.  Run `python manage.py migrate` to create the demo models.

4.  Run `python manage.py loaddata lazyloader_initial.json` to load the initial data for the live demo.

5.  Run `python manage.py collectstatic` to collect the static files of the live demo.

6.  To allow your models to be displayed by Django-Lazyloader, define a VALID_LAZY_MODELS variable in your settings.py
    file like this::

        VALID_LAZY_MODELS = [
            'MyApp.MyModel',
            'MyOtherApp.MyOtherModel',
        ]

7.  Create html templates and assign them to your models by adding a LAZY_TEMPLATES variable to your project's
    settings.py file like this::

        LAZY_TEMPLATES = {
            'MyApp.MyModel': 'myapp/mylazytemplate.html',
            'MyOtherApp.MyOtherModel': 'myotherapp/myotherlazytemplate.html'
        }


8.  Run the development server and visit http://localhost:8000/lazyloader/demo for the live demo.

9.  To access your the first 10 entries of your model 'Myapp.MyModel' in the JSON format visit
    http://localhost:8000/lazyloader/myapp-mymodel-json-0-10/

10. To access your the first 10 entries of your model 'Myapp.MyModel' in the HTML format visit
    http://localhost:8000/lazyloader/myapp-mymodel-html-0-10/

11. To create custom queries you can add the get parameters 'column' and 'search_value' to your url:
    http://localhost:8000/lazyloader/myapp-mymodel-html-0-10/?column=name&search_value=smith
    This url will execute a django-query that looks like this::

        MyApp.MyModel.objects.filter(name=smith)
