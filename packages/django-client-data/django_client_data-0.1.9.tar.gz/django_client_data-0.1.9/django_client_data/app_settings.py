from django.conf import settings


CLIENT_DATA_NAMESPACE = getattr(settings, 'CLIENT_DATA_NAMESPACE', 'DJANGO')
