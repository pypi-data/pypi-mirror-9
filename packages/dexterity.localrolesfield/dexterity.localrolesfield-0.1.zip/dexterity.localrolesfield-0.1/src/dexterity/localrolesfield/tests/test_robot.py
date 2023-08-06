# encoding: utf-8

from robotsuite import RobotTestSuite
from plone.testing import layered
from dexterity.localrolesfield import testing


def test_suite():
    return layered(RobotTestSuite('robot'),
                   layer=testing.LOCALROLESFIELD_ROBOT)
