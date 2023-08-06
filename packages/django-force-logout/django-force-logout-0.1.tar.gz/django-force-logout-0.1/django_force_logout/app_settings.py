from django.conf import settings

CALLBACK = getattr(settings, 'FORCE_LOGOUT_CALLBACK', 'path.to.logout.field')
