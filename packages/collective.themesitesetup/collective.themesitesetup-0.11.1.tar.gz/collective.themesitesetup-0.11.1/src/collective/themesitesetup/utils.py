# -*- coding: utf-8 -*-
from ConfigParser import SafeConfigParser
from collective.themesitesetup.interfaces import NO
from collective.themesitesetup.interfaces import PLUGIN_NAME
from collective.themesitesetup.interfaces import YES
from io import BytesIO
from plone.app.theming.interfaces import THEME_RESOURCE_NAME
from plone.app.theming.plugins.utils import getPlugins
from plone.resource.manifest import MANIFEST_FILENAME
import tarfile


# This is copied from p.a.theming.plugins.utils to get uncached data
# noinspection PyPep8Naming
def getPluginSettings(themeDirectory, plugins=None):
    """Given an IResourceDirectory for a theme, return the settings for the
    given list of plugins (or all plugins, if not given) provided as a list
    of (name, plugin) pairs.

    Returns a dict of dicts, with the outer dict having plugin names as keys
    and containing plugins settings (key/value pairs) as values.
    """

    if plugins is None:
        plugins = getPlugins()

    # noinspection PyPep8Naming
    manifestContents = {}

    if themeDirectory.isFile(MANIFEST_FILENAME):
        parser = SafeConfigParser()
        fp = themeDirectory.openFile(MANIFEST_FILENAME)

        try:
            parser.readfp(fp)
            for section in parser.sections():
                manifestContents[section] = {}

                for name, value in parser.items(section):
                    manifestContents[section][name] = value

        finally:
            try:
                fp.close()
            except AttributeError:
                pass

    pluginSettings = {}
    for name, plugin in plugins:
        pluginSettings[name] = manifestContents.get("%s:%s" % (THEME_RESOURCE_NAME, name), {})  # noqa

    return pluginSettings


# noinspection PyPep8Naming
def getSettings(themeDirectory):
    settings = getPluginSettings(themeDirectory, plugins=[(PLUGIN_NAME, None)])
    return settings.get(PLUGIN_NAME) or {}


# noinspection PyPep8Naming
def isEnabled(settings):
    return ((settings.get('enabled') or '').lower() not in NO
            and (settings.get('disabled') or '').lower() not in YES)


# noinspection PyPep8Naming
def populateTarball(tar, directory, prefix=''):
    for name in directory.listDirectory():
        if directory.isDirectory(name):
            # Create sub-directory
            info = tarfile.TarInfo(prefix + name)
            info.type = tarfile.DIRTYPE
            tar.addfile(info, BytesIO())

            # Populate sub-directory
            populateTarball(tar, directory[name], prefix + name + '/')
        else:
            data = directory.readFile(name)

            # Fix dotted names filtered by resource directory API
            if name.endswith('.dotfile'):
                name = '.' + name[:-8]

            info = tarfile.TarInfo(prefix + name)
            info.size = len(data)
            tar.addfile(info, BytesIO(data))


# noinspection PyPep8Naming
def createTarball(directory):
    fb = BytesIO()
    tar = tarfile.open(fileobj=fb, mode='w:gz')

    # Recursively populate tarball
    populateTarball(tar, directory)

    tar.close()
    return fb.getvalue()
