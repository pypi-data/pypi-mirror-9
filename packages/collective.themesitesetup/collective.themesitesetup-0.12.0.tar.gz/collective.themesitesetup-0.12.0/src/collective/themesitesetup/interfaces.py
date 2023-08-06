# -*- coding: utf-8 -*-
from zope.interface import Interface

PLUGIN_NAME = 'genericsetup'

DEFAULT_ENABLED_PROFILE_NAME = 'install'
DEFAULT_DISABLED_PROFILE_NAME = 'uninstall'

NO = ['off', 'false', 'no', '0']
YES = ['on', 'true', 'yes', '1']


class IGenericSetupExportableContainer(Interface):
    """Marker interface for exportable content"""
