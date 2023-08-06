from indicoio import JSON_HEADERS
from indicoio.utils import api_handler
import indicoio.config as config

def political(text, cloud=config.CLOUD, batch=False, auth=None, **kwargs):
    """
    Given input text, returns a probability distribution over the political alignment of the speaker.

    Example usage:

    .. code-block:: python

       >>> from indicoio import political
       >>> import numpy as np
       >>> text = 'Wish we had more bike lanes. \
       Hopefully, driverless cars will chance economics from ownership to fee for service.'
       >>> affiliation = political(text)
       >>> affiliation
       {u'Libertarian': 0.4923755446986322, u'Green': 0.2974443102818122,
       u'Liberal': 0.13730032938784784, u'Conservative': 0.07287981563170784}
       >>> least_like = affiliation.keys()[np.argmin(affiliation.values())]
       >>> most_like = affiliation.keys()[np.argmax(affiliation.values())]
       >>> 'This text is most like %s and least like %s'%(most_like,least_like)
       u'This text is most like Libertarian and least like Conservative'

    :param text: The text to be analyzed.
    :type text: str or unicode
    :rtype: Dictionary of party probability pairs
    """

    return api_handler(text, cloud=cloud, api="political", batch=batch, auth=auth, **kwargs)

def posneg(text, cloud=config.CLOUD, batch=False, auth=None, **kwargs):
    """
    Given input text, returns a scalar estimate of the sentiment of that text.
    Values are roughly in the range 0 to 1 with 0.5 indicating neutral sentiment.
    For reference, 0 suggests very negative sentiment and 1 suggests very positive sentiment.

    Example usage:

    .. code-block:: python

       >>> from indicoio import sentiment
       >>> text = 'Thanks everyone for the birthday wishes!! It was a crazy few days ><'
       >>> sentiment = sentiment(text)
       >>> sentiment
       0.6946439339979863

    :param text: The text to be analyzed.
    :type text: str or unicode
    :rtype: Float
    """

    return api_handler(text, cloud=cloud, api="sentiment", batch=batch, auth=auth, **kwargs)
