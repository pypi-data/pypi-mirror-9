import inspect, json, getpass, os
import requests
import numpy as np
from skimage.transform import resize

from indicoio import JSON_HEADERS
from indicoio import config

def api_handler(arg, cloud, api, batch=False, api_key=None, **kwargs):
    data = {'data': arg}
    data.update(**kwargs)
    json_data = json.dumps(data)
    if not cloud:
        cloud=config.cloud

    if cloud:
        host = "%s.indico.domains" % cloud
    else:
        # default to indico public cloud
        host = config.PUBLIC_API_HOST

    if not api_key:
        api_key = config.api_key

    url = config.url_protocol + "//%s/%s" % (host, api)
    url = url + "/batch" if batch else url
    url += "?key=%s" % api_key


    response = requests.post(url, data=json_data, headers=JSON_HEADERS)
    if response.status_code == 503 and cloud != None:
        raise Exception("Private cloud '%s' does not include api '%s'" % (cloud, api))

    json_results = response.json()
    results = json_results.get('results', False)
    if results is False:
        error = json_results.get('error')
        raise ValueError(error)
    return results


class TypeCheck(object):
    """
    Decorator that performs a typecheck on the input to a function
    """
    def __init__(self, accepted_structures, arg_name):
        """
        When initialized, include list of accepted datatypes and the
        arg_name to enforce the check on. Can totally be daisy-chained.
        """
        self.accepted_structures = accepted_structures
        self.is_accepted = lambda x: type(x) in accepted_structures
        self.arg_name = arg_name

    def __call__(self, fn):
        def check_args(*args, **kwargs):
            arg_dict = dict(zip(inspect.getargspec(fn).args, args))
            full_args = dict(arg_dict.items() + kwargs.items())
            if not self.is_accepted(full_args[self.arg_name]):
                raise DataStructureException(
                    fn,
                    full_args[self.arg_name],
                    self.accepted_structures
                )
            return fn(*args, **kwargs)
        return check_args


class DataStructureException(Exception):
    """
    If a non-accepted datastructure is passed, throws an exception
    """
    def __init__(self, callback, passed_structure, accepted_structures):
        self.callback = callback.__name__
        self.structure = str(type(passed_structure))
        self.accepted = [str(structure) for structure in accepted_structures]

    def __str__(self):
        return """
        function %s does not accept %s, accepted types are: %s
        """ % (self.callback, self.structure, str(self.accepted))


@TypeCheck((list, dict, np.ndarray), 'array')
def normalize(array, distribution=1, norm_range=(0, 1), **kwargs):
    """
    First arg is an array, whether that's in the form of a numpy array,
    a list, or a dictionary that contains the data in its values.

    Second arg is the desired distribution which would be applied before
    normalization.
        Supports linear, exponential, logarithmic and raising to whatever
        power specified (in which case you just put a number)

    Third arg is the range across which you want the data normalized
    """
    # Handling dictionary array input
    # Note: lists and numpy arrays behave the same in this program
    dict_array = isinstance(array, dict)

    if dict_array:
        keys = array.keys()
        array = np.array(array.values()).astype('float')
    else:  # Decorator errors if this isn't a list or a numpy array
        array = np.array(array).astype('float')

    # Handling various distributions
    if type(distribution) in [float, int]:
        array = np.power(array, distribution)
    else:
        array = getattr(np, distribution)(array, **kwargs)

    # Prep for normalization
    x_max, x_min = (np.max(array), np.min(array))

    def norm(element,x_min,x_max):
        base_span = (element - x_min)*(norm_range[-1] - norm_range[0])
        return norm_range[0] + base_span / (x_max - x_min)

    norm_array = np.vectorize(norm)(array, x_min, x_max)

    if dict_array:
        return dict(zip(keys, norm_array))
    return norm_array


def image_preprocess(image, batch=False):
    """
    Takes an image and prepares it for sending to the api including
    resizing and image data/structure standardizing.
    """
    if batch:
        return [image_preprocess(img, batch=False) for img in image]
    if isinstance(image,list):
        image = np.asarray(image)
    if type(image).__module__ != np.__name__:
        raise ValueError('Image was not of type numpy.ndarray or list.')
    if str(image.dtype) in ['int64','uint8']:
        image = image/255.
    if len(image.shape) == 2:
        image = np.dstack((image,image,image))
    if len(image.shape) == 4:
        image = image[:,:,:3]
    image = resize(image,(64,64))
    image = image.tolist()
    return image


def is_url(data, batch=False):
    if batch and isinstance(data[0], basestring):
        return True
    if not batch and isinstance(data, basestring):
        return True
    return False


