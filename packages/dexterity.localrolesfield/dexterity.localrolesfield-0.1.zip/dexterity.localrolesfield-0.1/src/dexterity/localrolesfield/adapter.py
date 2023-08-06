# encoding: utf-8

from borg.localrole.interfaces import ILocalRoleProvider
from dexterity.localroles.adapter import LocalRoleAdapter
from dexterity.localrolesfield.field import LocalRolesField
from plone.dexterity.interfaces import IDexterityFTI
from zope.component import getUtility
from zope.interface import implements


class LocalRoleFieldAdapter(LocalRoleAdapter):
    implements(ILocalRoleProvider)

    def getRoles(self, principal):
        """Grant permission for principal"""
        roles = list(super(LocalRoleFieldAdapter, self).getRoles(principal))
        for field, value in self.field_and_values_list:
            config = self.get_config(field).get(self.current_state)
            if not config:
                continue
            suffixes = self._get_suffixes_for_principal(config, value,
                                                        principal)
            for suffix in suffixes:
                roles.extend(config.get(suffix))

        return tuple(roles)

    def _get_suffixes_for_principal(self, config, value, principal):
        """Return the suffixes that match the given principal"""
        suffixes_principals = [(suffix, self._format_principal(value, suffix))
                               for suffix in config.keys()]
        return [s for s, p in suffixes_principals if p == principal]

    def getAllRoles(self):
        """Grant permissions"""
        for role in super(LocalRoleFieldAdapter, self).getAllRoles():
            yield role
        for field, value in self.field_and_values_list:
            state_config = self.get_config(field).get(self.current_state)
            if not state_config:
                continue
            for suffix, roles in state_config.items():
                yield (self._format_principal(value, suffix), tuple(roles))

    @staticmethod
    def _format_suffix(suffix):
        if not suffix:
            return u''
        return u'_{0}'.format(suffix)

    def _format_principal(self, principal, suffix):
        return u'{0}{1}'.format(principal, self._format_suffix(suffix))

    @property
    def field_and_values_list(self):
        """Return the id and the values of the LocalRolesField objects on the
        current context"""
        fti_schema = self.fti.lookupSchema()
        fields = [n for n, f in fti_schema.namesAndDescriptions(all=True)
                  if isinstance(f, LocalRolesField)]
        return [(f, v) for f in fields
                for v in getattr(self.context, f) or []]

    @property
    def fti(self):
        """Return the FTI"""
        return getUtility(IDexterityFTI, name=self.context.portal_type)

    def get_config(self, fieldname):
        """Return the config from FTI for a given fieldname"""
        return getattr(self.fti, fieldname, {})
