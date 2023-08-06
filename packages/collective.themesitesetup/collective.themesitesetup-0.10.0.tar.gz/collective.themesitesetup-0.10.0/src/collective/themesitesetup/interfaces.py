# -*- coding: utf-8 -*-
from zope.interface import Interface

DEFAULT_ENABLED_PROFILE_NAME = 'install'
DEFAULT_DISABLED_PROFILE_NAME = 'uninstall'


class IGenericSetupExportableContainer(Interface):
    """Marker interface for exportable content"""
