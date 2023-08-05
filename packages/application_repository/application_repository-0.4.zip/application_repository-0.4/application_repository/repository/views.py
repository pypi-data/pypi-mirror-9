from django_jsonrpc import jsonrpc_method
from django.shortcuts import redirect

import settings


@jsonrpc_method('api_version')
def api_version(request):
    return {'major': 0, 'minor': 2, 'micro': 0}


#@jsonrpc_method('available_packages')
def available_packages(package_class, request):
    return [p.name for p in package_class.objects.filter(public=True).order_by(
            'name')]


#@jsonrpc_method('package_latest_version')
def package_latest_version(version_class, request, package_name,
                           major_version=0):
    package_version = (version_class.objects
                       .filter(major=major_version, publish=True,
                               package__name=package_name)
                       .order_by('-major', '-minor', '-micro')[0])
    return {'major': package_version.major, 'minor': package_version.minor,
            'micro': package_version.micro}


#@jsonrpc_method('package_versions')
def package_versions(version_class, request, package_name, major_version=0):
    package_versions = (version_class.objects
                        .filter(major=major_version, publish=True,
                                package__name=package_name)
                        .order_by('major', 'minor', 'micro'))
    return [{'major': version.major, 'minor': version.minor,
             'micro': version.micro} for version in package_versions]


#@jsonrpc_method('package_url')
def package_url(version_class, request, package_name, version):
    package_version = version_class.objects.get(package__name=package_name,
            major=version['major'], minor=version['minor'],
                    micro=version['micro'])
    return str(package_version.url())


def redirect_to_latest(version_class, request, package_name, major_version=0):
    latest_version = package_latest_version(version_class, request,
                                            package_name, major_version)
    latest_url = package_url(version_class, request, package_name, latest_version)
    if latest_url.startswith('/'):
        latest_url = latest_url[1:]
    return redirect(getattr(settings, 'SITE_ROOT', '/') + latest_url)
