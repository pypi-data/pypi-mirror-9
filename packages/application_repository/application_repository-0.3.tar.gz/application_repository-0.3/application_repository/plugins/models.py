import re

from django.db import models
from path_helpers import path

import app_settings
from repository.models import Version, Package


cre_plugin_info = re.compile(r'''
        (?P<name>[a-zA-Z_]+)-
        (?P<major>\d+)\.(?P<minor>\d+)\.(?P<micro>\d+)
        \.tar\.gz''', re.VERBOSE)


class PluginVersion(Version):
    package = models.ForeignKey('Plugin')

    def url(self):
        plugin_path = self.path()
        plugin_url = path(app_settings.DATA_URL)
        return plugin_url.joinpath(plugin_path.name)

    def path(self):
        plugin_data_dir = path(app_settings.DATA_DIR)
        plugin_filename = '%s-%s.%s.%s.tar.gz' % (self.package.name, self.major,
                self.minor, self.micro)
        plugin_path = plugin_data_dir.joinpath(plugin_filename)

        if not plugin_path.isfile():
            raise ValueError, 'Plugin not found: %s' % plugin_path
        else:
            return plugin_path


class Plugin(Package):
    plugin_name = models.CharField(max_length=200)

    def __unicode__(self):
        return u'[%s] %s' % (self.name, self.plugin_name)
