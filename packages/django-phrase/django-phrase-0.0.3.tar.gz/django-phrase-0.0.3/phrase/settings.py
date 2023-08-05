from django.conf import settings

PHRASE_ENABLED = getattr(settings, 'PHRASE_ENABLED', True)
PHRASE_AUTH_TOKEN = getattr(settings, 'PHRASE_AUTH_TOKEN', '')
PHRASE_PREFIX = getattr(settings, 'PHRASE_PREFIX', '{{__')
PHRASE_SUFFIX = getattr(settings, 'PHRASE_SUFFIX', '__}}')
PHRASE_JS_HOST = getattr(settings, 'PHRASE_JS_HOST', 'phraseapp.com') 
PHRASE_JS_USE_SSL = getattr(settings, 'PHRASE_JS_USE_SSL', True) 
