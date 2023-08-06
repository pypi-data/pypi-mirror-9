import logging

from django.shortcuts import render
from django.core import serializers
from django.apps import apps
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse, Http404
from django.conf import settings
from django.template import loader, RequestContext, Context

logger = logging.getLogger(__name__)


def model_allowed(app_label, model_name):
    """
    This method checks whether the Model can be displayed or not
    """

    logger.debug('model_allowed function called.')

    ret_bool = False  # The return value

    # Check if 'VALID_LAZY_MODELS' is defined in the settings module
    if hasattr(settings, 'VALID_LAZY_MODELS'):
        # 'VALID_LAZY_MODELS' is defined. The settings value is assigned to the variable.
        valid_models = settings.VALID_LAZY_MODELS
    else:
        # Create an empty list if 'VALID_LAZY_MODELS' isn't defined
        valid_models = []

        logger.warning('VALID_LAZY_MODELS is not defined!')

    # Adds the demo model to the allowed models list
    valid_models.append('lazyloader.DemoObject')

    # Turns items in the list to lowercase to prevent faulty user input
    valid_models = [s.lower() for s in valid_models]

    # Turns model and app names to lowercase to prevent faulty user input
    model_lower = "{0}.{1}".format(app_label.lower(), model_name.lower())

    # Checks if the model is allowed by searching the 'valid_models' list for the model (both lowercase now)
    if model_lower in valid_models:
        ret_bool = True
        logger.debug('{0}.{1} is an allowed model.'.format(app_label, model_name))
    else:
        logger.debug('{0}.{1} is not an allowed model.'.format(app_label, model_name))

    return ret_bool


def get_template_path(app_label, model_name):
    """
    This method gets the appropriate HTML template for the model
    """

    logger.debug('get_template_path function called.')

    # Check if 'LAZY_TEMPLATES' is defined in the settings module
    if hasattr(settings, 'LAZY_TEMPLATES'):
        # 'LAZY_TEMPLATES' is defined. The settings value is assigned to the variable.
        templates = settings.LAZY_TEMPLATES
    else:
        # Create an empty dictionary if 'LAZY_TEMPLATES' isn't defined
        templates = {}

        logger.warning('LAZY_TEMPLATES is not defined!')

    # Adds the demo template to the dictionary. The key is the demo model
    templates['lazyloader.DemoObject'] = 'lazyloader/demo_html.html'

    # Sets all the keys in the dictionary to lowercase to prevent faulty user input
    templates_lower = dict((key.lower(), val) for key, val in templates.iteritems())

    # Turns model and app names to lowercase to prevent faulty user input
    model_lower = "{0}.{1}".format(app_label.lower(), model_name.lower())

    # Fetches the template
    template_to_display = templates_lower.get(model_lower)

    logger.debug('Loading template from ' + template_to_display)

    return template_to_display


def query_model(request, model):
    """
    This method defines the query
    """

    # The field that's being filtered
    column = request.GET.get('column')

    # The filter value
    search_value = request.GET.get('search_value')

    # Sets 'false' in string form to False.
    if search_value == 'false' or search_value == 'False':
        search_value = False

    # Exception handler for invalid values
    try:
        # Creates a query based on the parameters
        objects = model.objects.filter(**{column: search_value})

        logger.debug('Custom Query called: {0}.objects.filter({1}={2})'.format(model.__name__, column, search_value))
    except:
        # If the parameters are incorrect or nonexistent all objects are fetched
        objects = model.objects.all()

        logger.debug('No arguments for custom query found. Executed query: {0}.objects.all()'.format(model.__name__))

    return objects


def view_json(request, start, end, app_label, model_name):
    """
    The Method for the JSON view
    """

    logger.debug('view_json called. start: {0}, end: {1}, app_label: {2}, model_name: {3}'.format(start, end, app_label,
                                                                                                  model_name))

    # Only important for logging
    if start > end:
        logger.debug('Starting value is greater than end value')

    # Checks whether the model is allowed or not
    if model_allowed(app_label, model_name):
        # Searches models by name
        try:
            model = apps.get_model(app_label=app_label, model_name=model_name)
        except:
            raise Http404("Model doesn't exist")

        # Calls the custom query function
        objects = query_model(request, model)[start:end]

        # Creates JSON output for view
        data = serializers.serialize('json', objects)
    else:
        # Raise a HTTP404 if the object doesn't exist/isn't allowed
        raise Http404("Model not allowed")

    return HttpResponse(data, content_type='application/json')


def view_html(request, start, end, app_label, model_name):
    """
    The Method for the JSON view
    """

    logger.debug('view_html called. start: {0}, end: {1}, app_label: {2}, model_name: {3}'.format(start, end, app_label,
                                                                                                  model_name))
    logger.debug('Request method: ' + request.method)

    # Checks whether the model is allowed or not
    if model_allowed(app_label, model_name):
        # Searches models by name
        try:
            model = apps.get_model(app_label=app_label, model_name=model_name)
        except:
            raise Http404("Model doesn't exist")

        # Calls the custom query function
        objects = query_model(request, model)[start:end]

        # Assigns a template to the model
        template_path = get_template_path(app_label, model_name)

        # Load the template
        try:
            template = loader.get_template(template_path)
        except:
            logger.error('Template not found. Check the template path in your LAZY_TEMPLATES variable.')

            # Raises a HTTP404 if the template cannot be loaded
            raise Http404('Template not found.')
    else:
        logger.debug("Called model doesn't exist or isn't allowed.")

        # Raises a HTTP404 if the object isn't allowed or doesn't exist
        raise Http404("Object doesn't exist")

    context = RequestContext(request, {
        'objects': objects,
    })

    return HttpResponse(template.render(context))


def demo(request):
    """
    Loads the prepackaged demo
    """

    template = loader.get_template('lazyloader/demo.html')
    context = RequestContext(request)

    return HttpResponse(template.render(context))