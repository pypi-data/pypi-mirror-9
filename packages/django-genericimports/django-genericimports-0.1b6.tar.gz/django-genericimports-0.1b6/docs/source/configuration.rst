Setting up
==========

The setup of genericimports involves three parts: the actual mapping so you
can do your imports, the redis configuration and the logging which for
now is forced. If you are clever enough, yo can go straight into the
example_settings.py file which contains everything and includes an example
mapping commented.

For django
----------

Settings up redis
.................

Setting up the redis connection in django is easy, here is an example
configuration::

    RQ_QUEUES = {
        'importer': {
            'HOST': 'localhost',
            'PORT': 6379,
            'DB': 0,
            'PASSWORD': '',
            'DEFAULT_TIMEOUT': 360,
        },
    }

This will create a queue called "importer" connected to a local instance of
redis (this can be changed if you want to connect to a remote one). The rest
are just defaults that you can leave if you don't need to edit them.

Setting up the logging
......................

genericimports has a logging mechanism integrated, that stips out to a django
logger. If you don't have your logging activated, you should paste this and
it will create a file called "django.log" in the root of your project, that
way you can keep track of everything.

::

    LOGGING = {
        'version': 1,
        'disable_existing_loggers': False,

        'formatters': {
            'standard': {
                'format': "[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s",
                'datefmt': "%d/%b/%Y %H:%M:%S"
            },
        },

        'filters': {
            'require_debug_false': {
                '()': 'django.utils.log.RequireDebugFalse'
            }
        },

        'handlers': {
            'mail_admins': {
                'level': 'ERROR',
                'filters': ['require_debug_false'],
                'class': 'django.utils.log.AdminEmailHandler'
            },
            'logfile': {
                'level': 'DEBUG',
                'class': 'logging.handlers.RotatingFileHandler',
                'filename': BASE_DIR + "/django.log",
                'maxBytes': 2097152,  # 2MB per file
                'backupCount': 2,  # Store up to three files
                'formatter': 'standard',
            },
        },

        'loggers': {
            'django.request': {
                'handlers': ['mail_admins'],
                'level': 'ERROR',
                'propagate': True,
            },
            # Log all the things!
            '': {
                'handlers': ["logfile", ],
                'level': 'DEBUG',
            },
        }
    }

Setting up the mapping
......................

This is the most important part of the configuration, since it tells the script
where to go in your code to put the data in place, and example mapping looks
like this (copied from example_settings.py)

::

    IMPORTER = [
        {
            # Settings for the importer
            'settings': {
                # If you have a function that you want to apply after a successful
                # import, you would put it on the callback unbounded.
                'callback': 'MyFunction',
                # Who to send notifications about the imports
                'notifyto': 'example@example.com'
            },
            # This is the main mapping, the order or the items matter, since it
            # matches the column order in the CSV rows.
            'mapping': [
                {
                    'model': 'auth.User',
                    # Can we skip this data if it fails?
                    'optional': False,
                    # The field names match the column position (0, 1, 2 in this case)
                    'fields': [
                        'field_1',
                        'field_2',
                        'field_3',
                    ],
                    # We have fields that are not in the CSV but are required by the model
                    'unbound': {
                        'username': "(lambda x: ''.join(random.choice(string.ascii_lowercase) for _ in range(x)))(16)",
                        'password': "(lambda x: ''.join(random.choice(string.ascii_lowercase) for _ in range(x)))(16)", }
                },
                {
                    'model': 'accounts.UserProfile',
                    # Oh, this model is related to the other one, we put the
                    # position of that model in the import list and the field that
                    # links them.
                    'foreignkey': [0, 'user'],
                    'optional': False,
                    # Please note, user and profile share the first three columns
                    # of the CSV, you can do that.
                    'fields': [
                        'field_1',
                        'field_2',
                        'field_3',
                        'field_4',
                        'field_5',
                    ]
                },
                {
                    'model': 'accounts.UserSomethingRecord',
                    # Another model that is foreignkeyed to the user
                    'foreignkey': [0, 'user'],
                    # If for some reason this data of the row fails, we can skip it
                    'optional': True,
                    # Now, the data for this model is located after the first 9 columns
                    # so what we do is create 9 empty items, and then continue with
                    # our fields
                    'fields': [''] * 5 + [  # Note the multiplication, we skip 9 columns
                        'field_6',
                        'field_7',
                        'field_8',
                        # Imagine a thirdparty field here, django doesn't know how
                        # to handle it, but we know, so we call an unbound function
                        {'filter': my_function, 'name': "thirdparty_field"},
                    ]
                },
                # Now, for some reason we can have data for the same model that
                # repeats itself accross the columns (types of beer that you tried
                # for example)
                {
                    'model': 'accounts.UserBeers',
                    'foreignkey': [1, 'userprofile'],  # This links this object with the previous one
                    'optional': True,
                    'fields': [''] * 9 + [
                        'field_9',
                        'field_10',
                    ]
                },
                # Next record for beers
                {
                    'model': 'accounts.UserBeers',
                    'foreignkey': [1, 'userprofile'],  # This links this object with the previous one
                    'optional': True,
                    'fields': [''] * 11 + [
                        'field_11',
                        'field_12',
                    ]
                },
            ],
        }
    ]

For django CMS
--------------

Apart from the setting for django which you must do as well, you can add this application as an apphook to your CMS.
