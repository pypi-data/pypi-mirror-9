from django.conf import settings

import imp
from importlib import import_module
import logging
import os
import sys
import zipfile


logger = logging.getLogger('perseus')


def zip_dir(file_name):
    source_dir = getattr(settings, 'PERSEUS_SOURCE_DIR', None)
    if not source_dir:
        raise Exception('PERSEUS_SOURCE_DIR not defined in settings')

    if not os.path.isdir(source_dir):
        raise Exception('PERSEUS_SOURCE_DIR is not a valid directory')

    build_dir = getattr(settings, 'PERSEUS_BUILD_DIR', None)
    if not build_dir:
        raise Exception('PERSEUS_BUILD_DIR not defined in settings.')

    if not os.path.isdir(build_dir):
        os.makedirs(build_dir)

    rel_path = os.path.abspath(os.path.join(source_dir, os.pardir))

    file_path = os.path.abspath(os.path.join(build_dir, file_name))
    zip_file = zipfile.ZipFile(file_path, 'w')
    for root, dirs, files in os.walk(source_dir):
        for _file in files:
            location = os.path.join(root, _file)
            # path for file in zip archive
            zip_name = os.path.join(os.path.relpath(root, rel_path), _file)
            zip_file.write(location, arcname=zip_name)
            logger.debug('File: {0} added to {1}'.format(zip_name, file_name))
    zip_file.close()


def find_renderers():
    module_name = 'renderers'
    renderers = []
    modules_to_check = []

    # Hackish: do this in case we have some project top-level
    # (homepage, etc) urls defined project-level instead of app-level.
    settings_module = settings.SETTINGS_MODULE
    if settings_module:
        if "." in settings_module:
            # strip off '.settings" from end of module
            # (want project module, if possible)
            settings_module = settings_module.split(".", 1)[0]
        modules_to_check += [settings_module, ]

    # INSTALLED_APPS that aren't the project itself (also ignoring this
    # django_perseus module)
    modules_to_check += filter(
        lambda x: (x != "django_perseus") and (x != settings_module),
        settings.INSTALLED_APPS
    )

    for app in modules_to_check:
        try:
            import_module(app)
            app_path = sys.modules[app].__path__
        except AttributeError:
            logger.debug('Skipping app {0}.. (Not found)'.format(app))
            continue

        try:
            imp.find_module(module_name, app_path)
        except ImportError:
            logger.debug('Skipping app {0}.. (No \'renderers.py\')'.format(app))
            continue

        try:
            app_render_module = import_module('%s.%s' % (app, module_name))
            if hasattr(app_render_module, 'renderers'):
                renderers += getattr(app_render_module, module_name)
            else:
                logger.debug('Skipping app {0}.. (does not contain \'renderers var\''.format(app))
        except AttributeError:
            logger.debug('Skipping app \'{0}\'.. (Error importing \'{0}\')' % (app, app.renderers))
            continue

        logger.debug('Found renderers for \'{0}\'..'.format(app))
    return tuple(renderers)


def run_renderers():
    for render_cls in find_renderers():
        r = render_cls()
        r.generate()


def find_importers():
    importer_classes = []
    importers = getattr(settings, 'PERSEUS_IMPORTERS', None)
    if importers:
        for cls_path in importers:
            parts = cls_path.split('.')
            class_name = parts[-1]
            try:
                module = __import__('.'.join(parts[:-1]), fromlist=[''])

            except ImportError:
                raise Exception('{0} could not be found'.format(cls_path))

            _cls = getattr(module, class_name, None)
            if _cls:
                importer_classes.append(_cls)
    return importer_classes


def run_importers():
    importers = find_importers()
    for importer_cls in importers:
        importer_cls()
