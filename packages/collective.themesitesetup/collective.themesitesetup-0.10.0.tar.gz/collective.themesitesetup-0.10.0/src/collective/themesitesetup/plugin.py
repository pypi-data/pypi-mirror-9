# -*- coding: utf-8 -*-
from collective.themesitesetup.interfaces import DEFAULT_DISABLED_PROFILE_NAME
from collective.themesitesetup.interfaces import DEFAULT_ENABLED_PROFILE_NAME
from io import BytesIO
from plone import api
from plone.app.theming.interfaces import IThemePlugin
from plone.app.theming.interfaces import THEME_RESOURCE_NAME
from plone.resource.utils import queryResourceDirectory
from zope.interface import implements
import tarfile


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


# noinspection PyPep8Naming
class GenericSetupPlugin(object):
    """This plugin can be used to import generic setup profiles
    when theme is enabled or disabled.

    Relative directory paths for importable generic setup profiles can
    be defined in the theme manifest::

        [theme:genericsetup]
        install = profile
        uninstall =

    """

    implements(IThemePlugin)

    dependencies = ()

    def onDiscovery(self, theme, settings, dependenciesSettings):
        pass

    def onCreated(self, theme, settings, dependenciesSettings):
        pass

    def onEnabled(self, theme, settings, dependenciesSettings):
        res = queryResourceDirectory(THEME_RESOURCE_NAME, theme)
        if res is None:
            return

        directoryName = DEFAULT_ENABLED_PROFILE_NAME
        if 'install' in settings:
            directoryName = settings['install']

        directory = None
        if res.isDirectory(directoryName):
            directory = res[directoryName]

        if directory:
            tarball = createTarball(directory)
            portal_setup = api.portal.get_tool('portal_setup')
            portal_setup.runAllImportStepsFromProfile(
                None, purge_old=False, archive=tarball)

    def onDisabled(self, theme, settings, dependenciesSettings):
        res = queryResourceDirectory(THEME_RESOURCE_NAME, theme)
        if res is None:
            return

        directoryName = DEFAULT_DISABLED_PROFILE_NAME
        if 'uninstall' in settings:
            directoryName = settings['uninstall']

        directory = None
        if res.isDirectory(directoryName):
            directory = res[directoryName]

        if directory:
            tarball = createTarball(directory)
            portal_setup = api.portal.get_tool('portal_setup')
            portal_setup.runAllImportStepsFromProfile(
                None, purge_old=False, archive=tarball)

    def onRequest(self, request, theme, settings, dependenciesSettings):
        pass
