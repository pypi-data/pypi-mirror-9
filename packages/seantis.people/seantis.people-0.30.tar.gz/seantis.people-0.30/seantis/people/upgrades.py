# -*- coding: utf-8 -*-

from zope.component import getUtility
from zope.component.hooks import setSite

from plone import api
from plone.dexterity.interfaces import IDexterityFTI

from seantis.people import catalog_id
from seantis.people.supermodel.indexing import update_related_indexes


def import_profile(profile):
    setup = api.portal.get_tool('portal_setup')
    setup.runAllImportStepsFromProfile(profile)


def run_import_step_from_profile(step, module, profile):
    setup = api.portal.get_tool('portal_setup')
    profile = 'profile-{}:{}'.format(module, profile)
    setup.runImportStepFromProfile(profile, step)


def upgrade_portal_type(portal_type, module, profile):
    run_import_step_from_profile('typeinfo', module, profile)
    update_related_indexes(getUtility(IDexterityFTI, portal_type))


def install_custom_controlpanel(context):
    run_import_step_from_profile('controlpanel', 'seantis.people', 'default')


def upgrade_membership_title(context):
    upgrade_portal_type(
        'seantis.people.membership', 'seantis.people', 'default'
    )

    catalog = api.portal.get_tool('portal_catalog')
    memberships = catalog.unrestrictedSearchResults(
        portal_type='seantis.people.membership'
    )

    for membership in [m.getObject() for m in memberships]:
        if not hasattr(membership, 'role') or membership.role is None:
            membership.role = membership.title
            membership.title = membership.get_custom_title()
            membership.reindexObject()

            old_id = membership.id
            safe_title = membership.title.replace(u'ä', u'ae')
            safe_title = safe_title.replace(u'ö', u'oe')
            safe_title = safe_title.replace(u'ü', u'ue')

            new_id = safe_title.encode('ascii', 'ignore')
            new_id = new_id.lower().replace(' ', '-')
            membership.aq_inner.aq_parent.manage_renameObject(old_id, new_id)


def upgrade_phz_type_info(context):
    upgrade_portal_type('seantis.people.phz', 'seantis.people', 'phz')


def upgrade_standard_type_info(context):
    upgrade_portal_type('seantis.people.phz', 'seantis.people', 'standard')


def install_membership_dependencies(context):
    import_profile('profile-plone.formwidget.autocomplete:default')
    import_profile('profile-plone.app.relationfield:default')


def update_people_list(context):
    upgrade_portal_type('seantis.people.list', 'seantis.people', 'default')


def introduce_custom_catalog(context, profiles=None):
    run_import_step_from_profile('toolset', 'seantis.people', 'default')

    import_ctx = context._getImportContext('profile-seantis.people:default')
    old_site = api.portal.get()

    try:
        setSite(import_ctx.getSite())
        catalog = api.portal.get_tool(catalog_id)
        catalog.refreshCatalog(clear=1)
    finally:
        setSite(old_site)


def reindex_selectable_fields(context):
    # An unknown number of properties have change their type (from str to
    # unicode), we need to clear the catalogs first to avoid unicode exceptions
    # and rebuild it then to update the related indexes
    catalog = api.portal.get_tool('portal_catalog')
    catalog.manage_catalogClear()
    catalog.manage_catalogRebuild()

    catalog = api.portal.get_tool(catalog_id)
    catalog.manage_catalogClear()
    catalog.manage_catalogRebuild()


def enable_referenceablebehavior(context):
    catalog = api.portal.get_tool('portal_catalog')
    uid_catalog = api.portal.get_tool('uid_catalog')
    types = api.portal.get_tool('portal_types')
    portal = api.portal.get()

    for type_name in ('seantis.people.list', 'seantis.people.membership'):
        types[type_name].behaviors += (
            'plone.app.referenceablebehavior.referenceable.IReferenceable',)

        for brain in catalog.unrestrictedSearchResults(portal_type=type_name):
            obj = portal.unrestrictedTraverse(brain.getPath())
            uid_catalog.catalog_object(obj, brain.getPath())


def reindex_members(context):
    catalog = api.portal.get_tool(catalog_id)
    catalog.refreshCatalog(clear=1)
