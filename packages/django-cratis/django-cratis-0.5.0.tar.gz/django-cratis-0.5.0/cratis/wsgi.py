from configurations import importer
from cratis.cli import load_env

load_env()

importer.install()

import os
print os.environ['DJANGO_SETTINGS_MODULE']
try:
    from django.core.wsgi import get_wsgi_application
except ImportError:  # pragma: no cover
    from django.core.handlers.wsgi import WSGIHandler

    def get_wsgi_application():  # noqa
        return WSGIHandler()

# this is just for the crazy ones
application = get_wsgi_application()
