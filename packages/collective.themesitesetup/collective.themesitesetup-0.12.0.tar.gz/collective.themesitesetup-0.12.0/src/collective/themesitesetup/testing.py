# -*- coding: utf-8 -*-
from plone.app.robotframework.testing import AUTOLOGIN_LIBRARY_FIXTURE
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import PloneSandboxLayer
from plone.testing import z2


class CollectiveThemeSiteSetupLayer(PloneSandboxLayer):
    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        import collective.themesitesetup
        import collective.themesitesetup.tests
        self.loadZCML(package=collective.themesitesetup)
        self.loadZCML(package=collective.themesitesetup.tests)

    def setUpPloneSite(self, portal):
        self.applyProfile(portal, 'plone.app.theming:default')


COLLECTIVE_THEMESITESETUP_FIXTURE =\
    CollectiveThemeSiteSetupLayer()

COLLECTIVE_THEMESITESETUP_INTEGRATION_TESTING = IntegrationTesting(
    bases=(COLLECTIVE_THEMESITESETUP_FIXTURE,),
    name='Integration')
COLLECTIVE_THEMESITESETUP_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(COLLECTIVE_THEMESITESETUP_FIXTURE,),
    name='Functional')
COLLECTIVE_THEMESITESETUP_ROBOT_TESTING = FunctionalTesting(
    bases=(AUTOLOGIN_LIBRARY_FIXTURE,
           COLLECTIVE_THEMESITESETUP_FIXTURE,
           z2.ZSERVER_FIXTURE),
    name='Robot')
