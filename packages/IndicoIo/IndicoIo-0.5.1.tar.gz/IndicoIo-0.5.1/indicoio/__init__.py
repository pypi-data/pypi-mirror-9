from functools import partial

JSON_HEADERS = {'Content-type': 'application/json', 'Accept': 'text/plain'}

Version, version, __version__, VERSION = ('0.5.0',) * 4

from indicoio.text.sentiment import political, posneg
from indicoio.text.sentiment import posneg as sentiment
from indicoio.text.lang import language
from indicoio.text.tagging import text_tags
from indicoio.images.fer import fer
from indicoio.images.features import facial_features
from indicoio.images.features import image_features

apis = [
    'political',
    'posneg',
    'sentiment',
    'language',
    'fer',
    'facial_features',
    'image_features',
    'text_tags'
]
apis = dict((api, globals().get(api)) for api in apis)

for api in apis:
    globals()[api] = partial(apis[api])
    globals()['batch_' + api] = partial(apis[api], batch=True)
