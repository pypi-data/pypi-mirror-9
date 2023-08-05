import sys

from path_helpers import path
from django.core.exceptions import ObjectDoesNotExist

project_root = path(__file__).parent.parent.parent
sys.path.append(project_root)

from application.models import AppVersion, App, cre_app_info
from application import app_settings


def process_app_archive(app_path):
    match = cre_app_info.match(app_path.name)
    if match:
        major, minor, micro = int(match.group('major')),\
                int(match.group('minor')), int(match.group('micro'))

        app, created = App.objects.get_or_create(name=match.group(
                'name'))
        app_version, created = AppVersion.objects.get_or_create(
                package=app, major=major, minor=minor, micro=micro)
        if created:
            print 'Added App %s version %s.%s.%s' % (app.name, 
                    app_version.major, app_version.minor,
                            app_version.micro)


def scan_for_apps(apps_path):
    app_files = apps_path.files('*.msi')

    for app_path in app_files:
        process_app_archive(app_path)


if __name__ == '__main__':
    app_data_dir = app_settings.DATA_DIR
    print app_data_dir
    scan_for_apps(app_data_dir)
