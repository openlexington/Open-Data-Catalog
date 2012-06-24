import os, sys
sys.path.append(os.path.abspath(os.path.dirname(sys.argv[0])))
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

import django.core.handlers.wsgi

application = django.core.handlers.wsgi.WSGIHandler()
