=================
django-lumberjack
=================

Simple logging to the database for django projects.
Log entries are viewed in admin.

------------
Requirements
------------
Django 1.7 or greater.

-------
Install
-------
Install package::

    pip install django-lumberjack

Add ``'lumberjack'`` to your ``INSTALLED_APPS``::

    # settings.py
    
    INSTALLED_APPS = (
        'django.contrib.admin',
        'django.contrib.auth',
        ...
        'lumberjack',
    )

Add handler and logger configs::

    # settings.py

    LOGGING = {
        ...
        'handlers': {
            'lumberjack_handler': {
                'level': 'DEBUG',
                'class': 'lumberjack.handlers.DBHandler',
            },
        },
        'loggers': {
            'lumberjack': {
                'handlers': ['lumberjack_handler'],
            },
        }
    }

Create database tables::

    $ ./manage.py migrate lumberjack


-----
Usage
-----
Example of logging in a view function::

    # views.py

    import logging

    logger = logging.getLogger('lumberjack')

    def someview(request):
        
        logger.debug('someview was called', [__name__, 'sometag'])

        ...

        try: 
            # some action
            ...

        except:
            logger.error('some action failed', [__name__, 'fml'])

