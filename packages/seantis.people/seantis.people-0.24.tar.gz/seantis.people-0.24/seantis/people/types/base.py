from plone import api
from plone.dexterity.content import Container
from seantis.people.interfaces import IPerson
from seantis.people import _
from seantis.people import catalog_id


class PersonBase(Container):

    def _getCatalogTool(self):
        try:
            return api.portal.get_tool(catalog_id)
        except (api.exc.CannotGetPortalError, api.exc.InvalidParameterError):
            # it's possible that this is called during an update step, at
            # which point the seantis people catalog is not yet available
            return None

    @property
    def memberships(self):
        return IPerson(self).memberships()

    @property
    def organizations(self):
        if hasattr(self, 'test_organizations'):
            return self.test_organizations

        return IPerson(self).organizations()

    @property
    def organization_uuids(self):
        if hasattr(self, 'test_organization_uuids'):
            return self.test_organization_uuids

        return IPerson(self).organization_uuids()

    @property
    def membership_fields(self):
        return {
            'memberships': _(u'Memberships')
        }
