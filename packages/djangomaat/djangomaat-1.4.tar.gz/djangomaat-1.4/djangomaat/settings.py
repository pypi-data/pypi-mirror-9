from django.conf import settings

FLUSH_BATCH_SIZE = getattr(settings, 'MAAT_FLUSH_BATCH_SIZE', 1000)
