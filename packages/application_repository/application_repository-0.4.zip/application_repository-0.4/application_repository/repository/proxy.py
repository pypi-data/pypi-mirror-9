import urllib

from path_helpers import path
from jsonrpc import ServiceProxy


class PackageRepository(object):
    repository_name = None

    def __init__(self, server_url):
        if self.repository_name is None:
            raise NotImplementedError, 'repository_name must be set'
        self.server_url = server_url
        self._proxy = None
        self.proxy

    @property
    def proxy(self):
        if self._proxy is None:
            proxy = ServiceProxy(self.server_url + '/json/')
            self._proxy = proxy
        return getattr(self._proxy, self.repository_name)

    def api_version(self):
        return self._proxy.api_version()

    def available_packages(self):
        return self.proxy.available_packages()

    def latest_version(self, package_name):
        return self.proxy.package_latest_version(package_name)

    def versions(self, package_name):
        return self.proxy.package_versions(package_name)

    def package_url(self, package_name, package_version):
        return self.proxy.package_url(package_name, package_version)

    def latest_package_url(self, package_name):
        latest_version = self.proxy.package_latest_version(package_name)
        package_url = self.proxy.package_url(package_name, latest_version)
        return package_url

    def download_latest(self, package_name, output_dir):
        output_dir = path(output_dir)
        package_url = self.latest_package_url(package_name)
        package_full_url = '%s%s' % (self.server_url, package_url)
        data = urllib.urlopen(package_full_url).read()
        local_path = output_dir.joinpath(path(package_url).name)
        if not local_path.isfile():
            local_path.write_bytes(data)
            print 'Saved latest %s to %s' % (package_name, local_path)
        else:
            print 'File %s already exists - skipping download' % (local_path)
