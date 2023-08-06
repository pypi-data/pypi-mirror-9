indicoio-python
===============

A wrapper for a series of APIs made by indico.

Check out the main site on:

http://indico.io

Our APIs are totally free to use, and ready to be used in your
application. No data or training required.

Installation
------------

::

    pip install indicoio

Documentation
-------------

Available at `indico.reame.io <http://indico.readme.io/v1.0/docs>`__

Current APIs
------------

Right now this wrapper supports the following apps:

-  Positive/Negative Sentiment Analysis
-  Political Sentiment Analysis
-  Image Feature Extraction
-  Facial Emotion Recognition
-  Facial Feature Extraction
-  Language Detection
-  Text Topic Tagging

Examples
--------

::

    >>> import numpy as np

    >>> from indicoio import political, sentiment, fer, facial_features, language

    >>> political("Guns don't kill people. People kill people.")
    {u'Libertarian': 0.47740164630834825, u'Green': 0.08454409540443657, u'Liberal': 0.16617097211030055, u'Conservative': 0.2718832861769146}

    >>> sentiment('Worst movie ever.')
    {u'Sentiment': 0.07062467665597527}

    >>> sentiment('Really enjoyed the movie.')
    {u'Sentiment': 0.8105182526856075}

    >>> test_text = "Facebook blog posts about Android tech make better journalism than most news outlets."

    >>> tag_dict = text_tags(test_text)

    >>> sorted(tag_dict.keys(), key=lambda x: tag_dict[x], reverse=True)[:3]
    [u'startups_and_entrepreneurship', u'investment', u'business']

    >>> text_tags(test_text, threshold=0.1) # return only keys with value > 0.1
    {u'startups_and_entrepreneurship': 0.21888586688354486}

    >>> text_tags(test_text, top_n=1) # return only keys with top_n values
    {u'startups_and_entrepreneurship': 0.21888586688354486}

    >>> test_face = np.linspace(0,50,48*48).reshape(48,48).tolist()

    >>> fer(test_face)
    {u'Angry': 0.08843749137458341, u'Sad': 0.39091163159204684, u'Neutral': 0.1947947999669361, u'Surprise': 0.03443785859010413, u'Fear': 0.17574534848440568, u'Happy': 0.11567286999192382}

    >>> facial_features(test_face)
    [0.0, -0.02568680526917187, 0.21645604230056517, -0.1519435786033145, -0.5648621854611555, 3.0607368045577226, 0.11434321880792693, -0.02163810928547493, -0.44224330594186484, 0.3024315632285246, -2.6068048934495276, 2.497798330306638, 3.040558335205844, 0.741045340525325, 0.37198135618478817, -0.33132377802172325, -0.9804190889833034, 0.5046575784709395, -0.5609132323152847, 1.679107064439151, 0.6825037853544341, -1.5977176226648016, 1.8959464303080562, -0.7812860715595836, -2.998394007543733, -0.22637273967347724, -0.9642457010679496, 1.4557274834236749, 2.412244419186633, 2.3151771738421965, 0.7881483386786367, 1.6622850935863422, 0.1304768990234367, 1.9344501393866649, 3.1271558035162914, -0.10250886439220543, 1.4921395116492966, 2.761645355670677, 1.6903473594991179, 1.009209807271491, 0.07273926986120445, -1.4941708135718021, -2.082786362439631, 1.0160924044870847, 2.5326580674673895, -0.8328208491083264, 2.0390177029762935, 3.0342637531932777]

    >>> language_dict = language('Quis custodiet ipsos custodes')

    >>> sorted(language_dict.keys(), key=lambda x: language_dict[x], reverse=True)[:5]
    [u'Latin', u'Dutch', u'Greek', u'Portuguese', u'Spanish']

    >>> language_dict
    {u'Swedish': 0.00033330636691921914, u'Lithuanian': 0.007328693814717631, u'Vietnamese': 0.0002686116137658802, u'Romanian': 8.133913804076592e-06, ...}


    Batch API Access
    ----------------

    If you'd like to use our batch api interface, please send an email to contact@indico.io.

            from indicio import batch\_sentiment batch\_sentiment(['Text
            to analyze', 'More text'], auth=("example@example.com",
            "\*\*\*\*\*\*\*\*"))

::


    Authentication credentials can also be set as the environment variables "INDICO_USERNAME" and "INDICO_PASSWORD" or as 'username' and 'password' in the indicorc file.

    Private cloud API Access
    ------------------------

    If you're looking to use indico's API for high throughput applications, please contact contact@indico.io about our private cloud option.

            from indicio import sentiment sentiment("Text to analyze",
            cloud="example", auth=("example@example.com",
            "\*\*\*\*\*\*\*\*"))

::


    The `cloud` parameter redirects API calls to your private cloud hosted at [cloud].indico.domains. 

    Private cloud subdomains can also be set as the environment variable "INDICO_CLOUD" or as 'cloud' in the indicorc file.

    Configuration
    ------------------------

    Indicoio-python will search ./.indicorc and $HOME/.indicorc for the optional configuration file. Values in the local configuration file (./.indicorc) take precedence over those found in a global configuration file ($HOME/.indicorc). The indicorc file can be used to set an authentication username and password or a private cloud subdomain, so these arguments don't need to be specified for every api call. All sections are optional.

    Here is an example of a valid indicorc file:

[auth] username = test@example.com password = secret

[private\_cloud] cloud = example \`\`\`

Environment variables take precedence over any configuration found in
the indicorc file. The following environment variables are valid: -
$INDICO\_USERNAME - $INDICO\_PASSWORD - $INDICO\_CLOUD

Finally, any values explicitly passed in to an api call will override
configuration options set in the indicorc file or in an environment
variable.
