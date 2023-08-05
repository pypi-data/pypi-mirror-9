"""
Settings to use for development
"""
from settings import *

# Enable django-debug-toolbar for the following IPs
INTERNAL_IPS = ('127.0.0.1',)

# Test emails by looking at the console
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
