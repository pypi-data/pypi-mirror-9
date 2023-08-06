# encoding: utf-8

from dexterity.localroles.interfaces import IDexterityLocalRoles
from zope.schema.interfaces import IList


class IDexterityLocalRolesField(IDexterityLocalRoles):
    """Specific layer for the package"""


class ILocalRolesField(IList):
    """Local roles field"""
