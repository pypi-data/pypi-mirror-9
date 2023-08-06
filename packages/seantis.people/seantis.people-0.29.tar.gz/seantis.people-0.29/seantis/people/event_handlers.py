import logging
log = logging.getLogger('seantis.people')

from five import grok
from plone import api
from ZPublisher.interfaces import IPubBeforeCommit

from seantis.people import catalog_id


@grok.subscribe(IPubBeforeCommit)
def reindex_lists(event):
    """ seantis.people dynamically creates indexes and metadata to keep the
    list of people speedy. Depending on the type this may include an index
    of the organisation-memberships, which are available on the person and
    looked up using the catalog.

    During a clean & rebuild operation these memberships cannot be looked up
    because the index at this point may or may not contain the correct
    memberships (depending on the order of the content tree).

    To work around this issue, the catalog rebuild url is caught here. This
    url will be showing up in this method after the reindex happened.

    We then reindex just the organisations once more, knowing this time
    that the information in the catalog is up to date.

    """

    # never fail, this code is run after ever request!
    try:
        if event.request.URL.endswith('manage_catalogRebuild'):
            catalog = api.portal.get_tool(catalog_id)

            lists = catalog.unrestrictedSearchResults(
                portal_type='seantis.people.list'
            )

            for brain in lists:
                brain.getObject().reindex_organisations()

            log.info("organisation reindex successful")
    except Exception:
        log.exception("exception thrown during organisation reindex")
