from django.conf import settings


API_PARTNER_ID = getattr(settings, 'LEETCHI_API_PARTNER_ID', 'partnerID')
API_PRIVATE_KEY = getattr(settings, 'LEETCHI_API_PRIVATE_KEY', 'file://path/to/private_key')
API_PRIVATE_KEY_PASSWORD = getattr(settings, 'LEETCHI_API_PRIVATE_KEY_PASSWORD', '$ecret')
API_USE_SANDBOX = getattr(settings, 'LEETCHI_API_USE_SANDBOX', True)
API_HOST = getattr(settings, 'LEETCHI_API_HOST', None)

ALWAYS_SYNC = getattr(settings, 'LEETCHI_ALWAYS_SYNC', True)
