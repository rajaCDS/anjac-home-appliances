import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'anjac_home_appliances.settings')
application = get_wsgi_application()
