from indicoio.utils import api_handler
import indicoio.config as config

def text_tags(text, cloud=config.CLOUD, batch=False, auth=None, **kwargs):
    """
    Given input text, returns a probability distribution over 100 document categories

    Example usage:

    .. code-block:: python

       >>> import indicoio
       >>> import numpy as np
       >>> text = 'Monday: Delightful with mostly sunny skies. Highs in the low 70s.'
       >>> possible = indicoio.classification(text)
       >>> category = possible.keys()[np.argmax(possible.values())]
       >>> probability = np.max(possible.values())
       >>> "Predicted category '%s' with probability %.4f"%(category,probability)
       u'Predicted 'Weather' with probability 0.8548'

    :param text: The text to be analyzed.
    :type text: str or unicode
    :rtype: Dictionary of class probability pairs
    """

    return api_handler(text, cloud=cloud, api="texttags", batch=batch, auth=auth, **kwargs)
