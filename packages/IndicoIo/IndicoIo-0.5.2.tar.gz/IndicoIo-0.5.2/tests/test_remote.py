import unittest
import os
from requests import ConnectionError

import numpy as np
import skimage.io
from nose.plugins.skip import Skip, SkipTest

from indicoio import config
from indicoio import political, sentiment, fer, facial_features, language, image_features, text_tags
from indicoio import batch_political, batch_sentiment, batch_fer, batch_facial_features
from indicoio import batch_language, batch_image_features, batch_text_tags

DIR = os.path.dirname(os.path.realpath(__file__))

class BatchAPIRun(unittest.TestCase):

    def setUp(self):
        self.api_key = config.api_key
        config.url_protocol = "http:"

        if not all(self.api_key):
            raise SkipTest

    def tearDown(self):
        config.url_protocol = "https:"

    def test_batch_texttags(self):
        test_data = ["On Monday, president Barack Obama will be..."]
        response = batch_text_tags(test_data, api_key=self.api_key)
        self.assertTrue(isinstance(response, list))

    def test_batch_posneg(self):
        test_data = ['Worst song ever', 'Best song ever']
        response = batch_sentiment(test_data, api_key=self.api_key)
        self.assertTrue(isinstance(response, list))
        self.assertTrue(response[0] < 0.5)

    def test_batch_political(self):
        test_data = ["Guns don't kill people, people kill people."]
        response = batch_political(test_data, api_key=self.api_key)
        self.assertTrue(isinstance(response, list))

    def test_batch_fer(self):
        test_data = [np.random.rand(48, 48).tolist()]
        response = batch_fer(test_data, api_key=self.api_key)
        self.assertTrue(isinstance(response, list))
        self.assertTrue(isinstance(response[0], dict))

    def test_batch_facial_features(self):
        test_data = [np.random.rand(48, 48).tolist()]
        response = batch_facial_features(test_data, api_key=self.api_key)
        self.assertTrue(isinstance(response, list))
        self.assertTrue(isinstance(response[0], list))
        self.assertEqual(len(response[0]), 48)

    # TODO: uncomment this test once the remote server is updated to
    # deal with image_urls
    # def test_batch_image_urls(self):
    #     test_data = ['http://textfac.es/static/ico/favicon.png',
    #                  'http://textfac.es/static/ico/favicon.png']
    #     response = batch_facial_features(test_data, auth=self.auth)
    #     self.assertTrue(isinstance(response, list))
    #     self.assertTrue(isinstance(response[0], list))
    #     self.assertEqual(len(response[0]), 48)

    # TODO: add tests to test when one url is incorrect once we
    # have decided how we are dealing with them

    def test_batch_image_features_greyscale(self):
        test_data = [np.random.rand(64, 64).tolist()]
        response = batch_image_features(test_data, api_key=self.api_key)
        self.assertTrue(isinstance(response, list))
        self.assertTrue(isinstance(response[0], list))
        self.assertEqual(len(response[0]), 2048)

    def test_batch_image_features_rgb(self):
        test_data = [np.random.rand(64, 64, 3).tolist()]
        response = batch_image_features(test_data, api_key=self.api_key)
        self.assertTrue(isinstance(response, list))
        self.assertTrue(isinstance(response[0], list))
        self.assertEqual(len(response[0]), 2048)

    def test_batch_language(self):
        test_data = ['clearly an english sentence']
        response = batch_language(test_data, api_key=self.api_key)
        self.assertTrue(isinstance(response, list))
        self.assertTrue(response[0]['English'] > 0.25)

    def test_batch_set_cloud(self):
        test_data = ['clearly an english sentence']
        self.assertRaises(ConnectionError,
                          batch_language,
                          test_data,
                          api_key=self.api_key,
                          cloud='invalid/cloud')


class FullAPIRun(unittest.TestCase):

    def load_image(self, relpath, as_grey=False):
        image_path = os.path.normpath(os.path.join(DIR, relpath))
        image = skimage.io.imread(image_path, as_grey=True).tolist()
        return image

    def check_range(self, list, minimum=0.9, maximum=0.1, span=0.5):
        vector = np.asarray(list)
        self.assertTrue(vector.max() > maximum)
        self.assertTrue(vector.min() < minimum)
        self.assertTrue(np.ptp(vector) > span)

    def test_text_tags(self):
        text = "On Monday, president Barack Obama will be..."
        results = text_tags(text)
        max_keys = sorted(results.keys(), key=lambda x:results.get(x), reverse=True)
        assert 'political_discussion' in max_keys[:5]
        results = text_tags(text, top_n=5)
        assert len(results) is 5
        results = text_tags(text, threshold=0.1)
        for v in results.values():
            assert v >= 0.1

    def test_political(self):
        political_set = set(['Libertarian', 'Liberal', 'Conservative', 'Green'])
        test_string = "Guns don't kill people, people kill people."
        response = political(test_string)

        self.assertTrue(isinstance(response, dict))
        self.assertEqual(political_set, set(response.keys()))

        test_string = "pro-choice"
        response = political(test_string)

        self.assertTrue(isinstance(response, dict))
        assert response['Liberal'] > 0.25

    def test_posneg(self):
        test_string = "Worst song ever."
        response = sentiment(test_string)

        self.assertTrue(isinstance(response, float))
        self.assertTrue(response < 0.5)

        test_string = "Best song ever."
        response = sentiment(test_string)
        self.assertTrue(isinstance(response, float))
        self.assertTrue(response > 0.5)

    def test_good_fer(self):
        fer_set = set(['Angry', 'Sad', 'Neutral', 'Surprise', 'Fear', 'Happy'])
        test_face = np.random.rand(48,48).tolist()
        response = fer(test_face)

        self.assertTrue(isinstance(response, dict))
        self.assertEqual(fer_set, set(response.keys()))

    def test_happy_fer(self):
        test_face = self.load_image("data/happy.png", as_grey=True)
        response = fer(test_face)
        self.assertTrue(isinstance(response, dict))
        self.assertTrue(response['Happy'] > 0.5)

    def test_fear_fer(self):
        test_face = self.load_image("data/fear.png", as_grey=True)
        response = fer(test_face)
        self.assertTrue(isinstance(response, dict))
        self.assertTrue(response['Fear'] > 0.25)

    def test_bad_fer(self):
        fer_set = set(['Angry', 'Sad', 'Neutral', 'Surprise', 'Fear', 'Happy'])
        test_face = np.random.rand(56,56).tolist()
        response = fer(test_face)

        self.assertTrue(isinstance(response, dict))
        self.assertEqual(fer_set, set(response.keys()))

    def test_good_facial_features(self):
        test_face = np.random.rand(48,48).tolist()
        response = facial_features(test_face)

        self.assertTrue(isinstance(response, list))
        self.assertEqual(len(response), 48)
        self.check_range(response)

    # TODO: uncomment this test once the remote server is updated to
    # deal with image_urls
    # def test_image_url(self):
    #     test_face = 'http://textfac.es/static/ico/favicon.png'
    #     response = facial_features(test_face)

    #     self.assertTrue(isinstance(response, list))
    #     self.assertEqual(len(response), 48)
    #     self.check_range(response)

    def test_good_image_features_greyscale(self):
        test_image = np.random.rand(64, 64).tolist()
        response = image_features(test_image)

        self.assertTrue(isinstance(response, list))
        self.assertEqual(len(response), 2048)
        self.check_range(response)

    def test_good_image_features_rgb(self):
        test_image = np.random.rand(64, 64, 3).tolist()
        response = image_features(test_image)

        self.assertTrue(isinstance(response, list))
        self.assertEqual(len(response), 2048)
        self.check_range(response)

    def test_language(self):
        language_set = set([
            'English',
            'Spanish',
            'Tagalog',
            'Esperanto',
            'French',
            'Chinese',
            'French',
            'Bulgarian',
            'Latin',
            'Slovak',
            'Hebrew',
            'Russian',
            'German',
            'Japanese',
            'Korean',
            'Portuguese',
            'Italian',
            'Polish',
            'Turkish',
            'Dutch',
            'Arabic',
            'Persian (Farsi)',
            'Czech',
            'Swedish',
            'Indonesian',
            'Vietnamese',
            'Romanian',
            'Greek',
            'Danish',
            'Hungarian',
            'Thai',
            'Finnish',
            'Norwegian',
            'Lithuanian'
        ])
        language_dict = language('clearly an english sentence')
        self.assertEqual(language_set, set(language_dict.keys()))
        assert language_dict['English'] > 0.25

    def test_set_cloud(self):
        test_data = 'clearly an english sentence'
        self.assertRaises(ConnectionError,
                          language,
                          test_data,
                          cloud='invalid/cloud')

        temp_cloud = config.cloud
        config.cloud = 'invalid/cloud'

        self.assertEqual(config.cloud, 'invalid/cloud')
        self.assertRaises(ConnectionError,
                          language,
                          test_data)

        config.cloud = temp_cloud

        self.assertRaises(ConnectionError,
                          language,
                          test_data,
                          cloud='indico-test')

    def test_set_api_key(self):
        test_data = 'clearly an english sentence'
        self.assertRaises(ValueError,
                          language,
                          test_data,
                          api_key ='invalid_api_key')

        temp_api_key = config.api_key
        config.api_key = 'invalid_api_key'

        self.assertEqual(config.api_key, 'invalid_api_key')
        self.assertRaises(ValueError,
                          language,
                          test_data)

        config.api_key = temp_api_key



if __name__ == "__main__":
    unittest.main()
