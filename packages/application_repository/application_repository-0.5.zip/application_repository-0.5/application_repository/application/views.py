from django_jsonrpc import jsonrpc_method

from .models import App as package_class, AppVersion as version_class

import repository.views 


@jsonrpc_method('application.available_packages')
def available_packages(request):
    return repository.views.available_packages(package_class, request)


@jsonrpc_method('application.package_latest_version')
def package_latest_version(request, package_name):
    return repository.views.package_latest_version(version_class, request,
            package_name)


@jsonrpc_method('application.package_versions')
def package_versions(request, package_name):
    return repository.views.package_versions(version_class, request, package_name)


@jsonrpc_method('application.package_url')
def package_url(request, package_name, version):
    return repository.views.package_url(version_class, request, package_name,
            version)


def redirect_to_latest(request, package_name):
    return repository.views.redirect_to_latest(version_class, request,
            package_name)
