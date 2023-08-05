from ..repository.proxy import PackageRepository


class PluginRepository(PackageRepository):
    repository_name = 'plugins'

    def latest_version(self, package_name, app_version=None):
        if app_version is None:
            return super(PluginRepository, self).latest_version(package_name)
        return self.proxy.package_latest_version_for_app_version(package_name,
                                                                 app_version)

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
