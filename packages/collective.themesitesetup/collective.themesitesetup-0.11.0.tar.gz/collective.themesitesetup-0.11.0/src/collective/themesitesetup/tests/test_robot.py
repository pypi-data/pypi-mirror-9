# -*- coding: utf-8 -*-
from collective.themesitesetup.testing import COLLECTIVE_THEMESITESETUP_ROBOT_TESTING  # noqa
from plone.testing import layered
import robotsuite
import unittest


def test_suite():
    suite = unittest.TestSuite()
    suite.addTests([
        layered(robotsuite.RobotTestSuite("test_export.robot"),
                layer=COLLECTIVE_THEMESITESETUP_ROBOT_TESTING),
        layered(robotsuite.RobotTestSuite("test_import.robot"),
                layer=COLLECTIVE_THEMESITESETUP_ROBOT_TESTING),
        layered(robotsuite.RobotTestSuite("test_enabled.robot"),
                layer=COLLECTIVE_THEMESITESETUP_ROBOT_TESTING),
        layered(robotsuite.RobotTestSuite("test_disabled.robot"),
                layer=COLLECTIVE_THEMESITESETUP_ROBOT_TESTING),
    ])
    return suite
