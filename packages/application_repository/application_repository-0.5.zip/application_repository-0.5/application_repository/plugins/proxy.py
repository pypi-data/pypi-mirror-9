import urllib
import logging
from copy import copy

from path_helpers import path

from ..repository.proxy import PackageRepository


class PluginRepository(PackageRepository):
    repository_name = 'plugins'

    def available_packages(self, app_version=None):
        packages = super(PluginRepository, self).available_packages()
        if app_version:
            logging.info('available_packages(app_version=%s.%s.%s)' % 
                         (app_version['major'], app_version['minor'],
                          app_version['micro']))
            for p in copy(packages): # need to make a copy of the packages list
                                     # because we are removing elements while
                                     # iterating through it
                try:
                    self.latest_version(p, app_version)
                except:
                    packages.remove(p)
        else:
            logging.info('available_packages(app_version=%s):' % app_version)
        return packages

    def latest_version(self, package_name, app_version=None):
        if app_version is None:
            version = super(PluginRepository, self).latest_version(package_name)
            logging.info('latest_version(package_name=%s, app_verison=%s)'
                         '=%s' % (package_name, app_version, version['major'],
                         version['minor'], version['micro']))
        else:
            version = self.proxy.package_latest_version_for_app_version(
                package_name, app_version)
            logging.info('latest_version(package_name=%s, app_verison=%s.%s.%s)'
                         '=%s.%s.%s' % (package_name, app_version['major'],
                         app_version['minor'], app_version['micro'],
                         version['major'], version['minor'], version['micro']))
        return version

    def latest_package_url(self, package_name, app_version=None):
        latest_version = self.latest_version(package_name, app_version)
        package_url = self.proxy.package_url(package_name, latest_version)
        return package_url

    def download_latest(self, package_name, output_dir, app_version=None):
        output_dir = path(output_dir)
        package_url = self.latest_package_url(package_name, app_version)
        package_full_url = '%s%s' % (self.server_url, package_url)
        data = urllib.urlopen(package_full_url).read()
        local_path = output_dir.joinpath(path(package_url).name)
        if not local_path.isfile():
            local_path.write_bytes(data)
            print 'Saved latest %s to %s' % (package_name, local_path)
        else:
            print 'File %s already exists - skipping download' % (local_path)
