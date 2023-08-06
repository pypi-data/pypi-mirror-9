from indicoio.utils import api_handler
import indicoio.config as config

def language(text, cloud=None, batch=False, api_key=None, **kwargs):
    """
    Given input text, returns a probability distribution over 33 possible
    languages of what language the text was written in.

    Example usage:

    .. code-block:: python

       >>> import indicoio
       >>> import numpy as np
       >>> text = 'Monday: Delightful with mostly sunny skies. Highs in the low 70s.'
       >>> possible = indicoio.language(text)
       >>> language = possible.keys()[np.argmax(possible.values())]
       >>> probability = np.max(possible.values())
       >>> 'Predicted %s with probability %.4f'%(language,probability)
       u'Predicted English with probability 0.8548'

    :param text: The text to be analyzed.
    :type text: str or unicode
    :rtype: Dictionary of language probability pairs
    """

    return api_handler(text, cloud=cloud, api="language", batch=batch, api_key=api_key, **kwargs)
