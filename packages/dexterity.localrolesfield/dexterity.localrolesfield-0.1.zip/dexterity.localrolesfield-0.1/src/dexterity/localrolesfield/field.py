# encoding: utf-8

from dexterity.localrolesfield.interfaces import ILocalRolesField
from zope import schema
from zope.interface import implementer


@implementer(ILocalRolesField)
class LocalRolesField(schema.List):
    """
    """
