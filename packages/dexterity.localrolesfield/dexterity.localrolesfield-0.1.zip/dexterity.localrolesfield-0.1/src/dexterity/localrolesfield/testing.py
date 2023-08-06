# encoding: utf-8

from dexterity.localrolesfield.field import LocalRolesField
from plone import api
from plone.app.robotframework.testing import AUTOLOGIN_LIBRARY_FIXTURE
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PloneWithPackageLayer
from plone.app.testing import ploneSite
from plone.dexterity.content import Item
from plone.supermodel import model
from plone.testing import z2
from zope import interface
from zope.schema import Choice
from zope.schema.fieldproperty import FieldProperty
from zope.schema.vocabulary import SimpleVocabulary

import dexterity.localrolesfield as package


class ITestingType(model.Schema):

    localrole_field = LocalRolesField(
        title=u'localrolefield',
        required=False,
        value_type=Choice(vocabulary=SimpleVocabulary.fromValues([u'support',
                                                                  u'mail'])),
    )

    localrole_user_field = LocalRolesField(
        title=u'localroleuserfield',
        required=False,
        value_type=Choice(vocabulary=SimpleVocabulary.fromValues([u'john',
                                                                  u'jane',
                                                                  u'tom',
                                                                  u'kate'])),
    )


class TestingType(Item):
    interface.implements(ITestingType)

    localrole_field = FieldProperty(ITestingType[u'localrole_field'])


class LocalRolesFieldLayer(PloneWithPackageLayer):

    def setUp(self):
        super(LocalRolesFieldLayer, self).setUp()
        with ploneSite() as portal:
            groups_tool = portal.portal_groups
            groups = {'mail_editor': ('john', 'jane'),
                      'mail_reviewer': ('jane', 'tom'),
                      'support_reviewer': ('kate', )}
            for group_id in groups:
                if group_id not in groups_tool.getGroupIds():
                    groups_tool.addGroup(group_id)
                for user in groups[group_id]:
                    if not api.user.get(username=user):
                        api.user.create(username=user, email='test@test.com')
                    api.group.add_user(groupname=group_id, username=user)
            if not api.user.get(username='basic-user'):
                api.user.create(username='basic-user', email='test@test.com')


LOCALROLESFIELD_FIXTURE = LocalRolesFieldLayer(
    zcml_filename='testing.zcml',
    zcml_package=package,
    gs_profile_id='dexterity.localrolesfield:testing',
    name='dexterity.localrolesfield.layer:fixture',
)

LOCALROLESFIELD_INTEGRATION = IntegrationTesting(
    bases=(LOCALROLESFIELD_FIXTURE, ),
    name='dexterity.localrolesfield.layer:integration',
)

LOCALROLESFIELD_FUNCTIONAL = FunctionalTesting(
    bases=(LOCALROLESFIELD_FIXTURE, ),
    name='dexterity.localrolesfield.layer:functional',
)

LOCALROLESFIELD_ROBOT = FunctionalTesting(
    bases=(LOCALROLESFIELD_FIXTURE, AUTOLOGIN_LIBRARY_FIXTURE,
           z2.ZSERVER_FIXTURE),
    name='dexterity.localrolesfield.layer:robot',
)
