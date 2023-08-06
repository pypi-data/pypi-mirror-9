import os
from StringIO import StringIO

import ConfigParser

class Settings(ConfigParser.ConfigParser):

    def __init__(self, *args, **kwargs):
        """
        files: filepaths or open file objects
        """
        self.files = kwargs.pop('files')

        ConfigParser.ConfigParser.__init__(self, *args, **kwargs)

        for fd in self.files:
            try:
                self.readfp(fd)
            except AttributeError: 
                self.read(fd)

        self.auth_settings = self.get_section('auth')
        self.private_cloud_settings = self.get_section('private_cloud')

    def get_section(self, section):
        """
        Retrieve a ConfigParser section as a dictionary, default to {}
        """
        try:
            return dict(self.items(section))
        except ConfigParser.NoSectionError:
            return {}

    def cloud(self):
        return (
            os.getenv("INDICO_CLOUD") or 
            self.private_cloud_settings.get('cloud') or 
            None
        )

    def auth(self):
        return (
            os.getenv("INDICO_USERNAME") or self.auth_settings.get('username'),
            os.getenv("INDICO_PASSWORD") or self.auth_settings.get('password')
        )

SETTINGS = Settings(files=[
    os.path.expanduser("~/.indicorc"),
    os.path.join(os.getcwd(), '.indicorc')
])

AUTH = SETTINGS.auth()
CLOUD = SETTINGS.cloud()
PUBLIC_API_HOST = 'apiv1.indico.io'
