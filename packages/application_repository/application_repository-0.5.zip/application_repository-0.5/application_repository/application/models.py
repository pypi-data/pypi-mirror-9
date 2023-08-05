import re

from django.db import models
from path_helpers import path

import app_settings
from repository.models import Version, Package


cre_app_info = re.compile(r'''
        (?P<name>microdrop)-
        (?P<major>\d+)\.(?P<minor>\d+)\.(?P<micro>\d+)
        \.msi''', re.VERBOSE)


class AppVersion(Version):
    package = models.ForeignKey('App')

    def url(self):
        app_path = self.path()
        app_url = path(app_settings.DATA_URL)
        return app_url.joinpath(app_path.name)

    def path(self):
        app_data_dir = path(app_settings.DATA_DIR)
        app_filename = '%s-%s.%s.%s.msi' % (self.package.name, self.major,
                self.minor, self.micro)
        app_path = app_data_dir.joinpath(app_filename)

        if not app_path.isfile():
            raise ValueError, 'Application not found: %s' % app_path
        else:
            return app_path


class App(Package):
    pass
