Okapi
=====

Python Library to send API info to Storage Server


Okapi setup 
===========
In an existing project you should at least modify the following files:


requirements/base.txt
---------------------
Add the following requirement to the project's settings. It won't be needed to
add ``requests`` if the project is already using it.
``requests`` version should be >= 2.2.11:

.. code-block:: python

    okapi==X.Y.Z


settings.py
-----------
Add the following configuration to the project's settings:

.. code-block:: python    

    ########## OKAPI CONFIGURATION
    OKAPI_PROJECT = 'your-project-name'

    OKAPI_URI = None
    if settings.has_section('okapi'):
        OKAPI_URI = 'mongodb://{0},{1},{2}/{3}?replicaSet={4}'.format(

            settings.get('okapi', 'host0'),
            settings.get('okapi', 'host1'),
            settings.get('okapi', 'host2'),
            settings.get('okapi', 'name'),
            settings.get('okapi', 'replica'),
        )

    ########## END OKAPI CONFIGURATION

Note that if the project is already using *MongoDB*, you shouldn't store Okapi's
data into the same database. Okapi creates collections dynamically and could
conflict with your the  project's.


Initialization
--------------
Initialize Okapi in the ``models.py`` file of a basic application of the project.
This way Okapi will be imported at startup time:

.. code-block:: python

    import requests    
    from django.conf import settings    

    from okapi.api import Api

    project_name = getattr(settings, 'OKAPI_PROJECT')
    mongodb_uri = getattr(settings, 'MONGODB_URI')
    okapi_client = Api(project_name, requests, mongodb_uri)


Usage
-----
Once initialized you can use Okapi wherever you use ``requests`` library.
Think of Okapi as if you were using ``requests`` because they both have the same
API.

Requests documentation: http://docs.python-requests.org/en/latest/


Activating/deactivating okapi in your project
---------------------------------------------
In the file ``settings/base.py`` under the ``OKAPI CONFIGURATION`` section, you 
can add a boolean setting in order to enable/disable okapi for your project. It 
could be interesting to have it enabled in QA or staging environment and after
it has been properly tested, activate it also in production.

You can have a section into ``your-project-name/settings/dev.py``: 

.. code-block:: python

    ########## OKAPI CONFIGURATION
    OKAPI_ENABLED = True
    ########## END OKAPI CONFIGURATION

Another one into ``your-project-name/settings/production.py``: 

.. code-block:: python    

    ########## OKAPI CONFIGURATION
    OKAPI_ENABLED = False
    ########## END OKAPI CONFIGURATION

And so on. Note that ``get_custom_setting`` is a wrapper around ``getattr``. 
Then you could initialize it conditionally as shown below:

.. code-block:: python

    http_lib = requests
    if (get_custom_setting('OKAPI_ENABLED') and okapi_uri is not None):
        project_name = get_custom_setting('OKAPI_PROJECT', required=True)
        okapi_uri = get_custom_setting('OKAPI_URI', required=True)
        okapi_client = Api(project_name, requests, okapi_uri)
        http_lib = okapi_client

