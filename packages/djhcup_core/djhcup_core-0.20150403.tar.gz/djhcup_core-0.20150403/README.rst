=====
HCUP Hachoir: Core module
=====

Part of the Django-HCUP Hachoir set of Python packages. Provides core functionality, including automated detection and configuration of other installed djhcup components.

Quick start
-----------

0. HCUP Hachoir uses Celery (http://www.celeryproject.org/) as a tasking layer by default. Be sure you have properly configured your Django installation to use Celery, including a message broker and result backend. Typically this invovles creating a celery.py file as described in http://celery.readthedocs.org/en/latest/django/first-steps-with-django.html, and adding configuration items to your settings.py file.

For example, with a local rabbitmq-server back-end, add these lines::

    BROKER_URL = 'amqp://'
    CELERY_RESULT_BACKEND = 'amqp://'

1. Add "djhcup_core" to your INSTALLED_APPS setting like this::

      INSTALLED_APPS = (
          ...
          'djhcup_core',
      )

2. Modify your urls.py to include the following pattern entry::

    url(r'', include('djhcup_core.urls'))
    
If you want all djhcup addresses to appear as a subdirectory instead, such as www.example.com/your_prefix/, change r'' to r'your_prefix'::

    url(r'your_prefix', include('djhcup_core.urls'))

3. Modify your settings.py to include a separate database dictionary entry for djhcup named 'djhcup'. For example::

    'djhcup': {
            'ENGINE': 'django.db.backends.postgresql_psycopg2',
            'NAME': 'your_db_name',
            'USER': 'your_db_user',
            'PASSWORD': 'your_db_password',
            'HOST': 'your_db_host',
            'PORT': '5432',
        },
    
Note that while this could use the same database and credentials as your default entry, we recommend you set it up in a separate database for easier management.

4. Tell djhcup where to look for your HCUP data by adding these lines to your settings.py::

    import os, pyhcup
    # Look in here for data and loadfiles
    DJHCUP_IMPORT_PATHS = [
                        '/path/to/your/hcup/data/', # update this to point at your raw data
                        os.path.dirname(pyhcup.__file__), # loadfiles included with PyHCUP
                        ]
    
5. Run `python manage.py syncdb` to create the djhcup_staging models. Or, if using South, migrate forward to build database objects for this package's models.

6. Start your server per normal (for test servers, use `python manage.py runserver`).
