# encoding: utf-8

from collective.z3cform.datagridfield import DictRow
from dexterity.localroles import _ as LRMF
from dexterity.localroles.browser.settings import LocalRoleConfigurationForm
from dexterity.localroles.browser.settings import LocalRoleConfigurationPage
from dexterity.localroles.browser.settings import LocalRoleList
from dexterity.localroles.browser.settings import Role
from dexterity.localroles.browser.settings import WorkflowState
from dexterity.localroles.vocabulary import plone_role_generator
from dexterity.localrolesfield import _
from dexterity.localrolesfield.field import LocalRolesField
from z3c.form import field
from zope.interface import Interface
from zope.schema import Choice
from zope.schema import TextLine


class ILocalRoleConfig(Interface):
    state = WorkflowState(title=LRMF(u'state'), required=True)

    value = TextLine(title=_(u'suffix'), required=False, default=u'')

    roles = Role(title=LRMF(u'roles'),
                 value_type=Choice(source=plone_role_generator),
                 required=True)


class LocalRoleFieldConfigurationForm(LocalRoleConfigurationForm):

    @property
    def fields(self):
        fields = super(LocalRoleFieldConfigurationForm, self).fields
        fields = fields.values()

        schema_fields = []
        fti_schema = self.context.fti.lookupSchema()
        for name, fti_field in fti_schema.namesAndDescriptions(all=True):
            if isinstance(fti_field, LocalRolesField):
                f = LocalRoleList(
                    __name__=str(name),
                    title=fti_field.title,
                    description=fti_field.description,
                    value_type=DictRow(title=u"fieldconfig",
                                       schema=ILocalRoleConfig)
                )
                schema_fields.append(f)
        schema_fields = sorted(schema_fields, key=lambda x: x.title)
        fields.extend(schema_fields)

        return field.Fields(*fields)


class LocalRoleFieldConfigurationPage(LocalRoleConfigurationPage):
    form = LocalRoleFieldConfigurationForm
