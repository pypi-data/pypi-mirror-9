import sys
import tarfile
import logging


import yaml
from path_helpers import path
from django.core.exceptions import ObjectDoesNotExist

project_root = path(__file__).parent.parent.parent
sys.path.append(project_root)

from plugins.models import PluginVersion, Plugin, cre_plugin_info


def process_plugin_archive(plugin_path):
    match = cre_plugin_info.match(plugin_path.name)
    if match:
        major, minor, micro = int(match.group('major')),\
                int(match.group('minor')), int(match.group('micro'))

        t = tarfile.open(plugin_path)
        properties_path = [path(p) for p in t.getnames() if 'properties.yml' in p][0]
        properties = yaml.load(t.extractfile(properties_path).read())

        plugin_name = properties.get('plugin_name', match.group('name'))
        plugin, created = Plugin.objects.get_or_create(name=match.group(
                'name'))
        plugin.plugin_name = plugin_name
	plugin.save()
        plugin_version, created = PluginVersion.objects.get_or_create(
                package=plugin, major=major, minor=minor, micro=micro)
        if created:
            print 'Added Plugin %s version %s.%s.%s' % (plugin.name, 
                    plugin_version.major, plugin_version.minor,
                            plugin_version.micro)


def scan_for_plugins(plugins_path):
    plugin_files = sorted(plugins_path.files('*.tar.gz'))

    for plugin_path in plugin_files:
        try:
            process_plugin_archive(plugin_path)
        except ValueError, why:
            logging.warning('skipping plugin archive %s:\n%s' % (plugin_path,
                why))


if __name__ == '__main__':
    logging.basicConfig(format='[%(levelname)s] %(message)s', level=logging.WARNING)
    scan_for_plugins(project_root.joinpath('plugin_data'))
