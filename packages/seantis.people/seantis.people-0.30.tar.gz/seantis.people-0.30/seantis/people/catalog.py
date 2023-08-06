from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import search_zcatalog as SearchZCatalog
from Globals import InitializeClass
from plone import api
from Products.CMFPlone.CatalogTool import CatalogTool
from Products.ZCatalog.ZCatalog import ZCatalog
from Products.ZCTextIndex.ZCTextIndex import PLexicon
from Products.ZCTextIndex.PipelineFactory import element_factory
from seantis.people import catalog_id, log
from seantis.people.interfaces import IPeopleCatalog
from zope.interface import implements


class Extra(object):
    pass


class PeopleCatalog(CatalogTool):
    """ A custom catalog for seantis.people. Required because people may have
    a large number of metadata/indices assigned to them which would slow
    down the rest of the site.

    The catalog is used by all types that inherit from
    seantis.people.types.base.PersonBase. It is supposed to shadow the
    portal_catalog. It does so by applying indexing operations to both itself
    and the portal_catalog.

    This results in a separate catalog that has the same indexes and metadata
    as the portal_catalog plus additional indexes and metadata defined by the
    custom people types.

    This catalog can be used if all that is required is a lookup to people
    indexes/properties - like when displaying the list of people. Anything
    else should still go through portal_catalog.

    Note that the people catalog is automatically update if you work with
    seantis people objects. But you have to use it manually if you need
    to get a custom index/metadata value:

        from plone import api
        from seantis.people import catalog_id

        people_catalog = api.portal.get_tool(catalog_id)

    """

    implements(IPeopleCatalog)

    title = "Seantis People Catalog"
    id = catalog_id
    portal_type = meta_type = 'PeopleCatalog'
    plone_tool = 1

    security = ClassSecurityInfo()
    security.declarePrivate('indexObject')
    security.declarePrivate('reindexObject')
    security.declarePrivate('unindexObject')
    security.declarePrivate('setup_lexicons')
    security.declarePrivate('setup_indexes')
    security.declarePrivate('setup_metadata')
    security.declareProtected(SearchZCatalog, 'searchResults')

    _properties = (
        {'id': 'title', 'type': 'string', 'mode': 'w'},
    )

    def __init__(self):
        ZCatalog.__init__(self, self.id)

        self.setup_lexicons()
        self.setup_indexes()
        self.setup_metadata()

        # the catalog needs to be cleared after setting up everything
        # or subtle errors will appear (like print failing on brains)
        self._catalog.clear()
        self._catalog.updateBrains()

    @property
    def base_catalog(self):
        return api.portal.get_tool('portal_catalog')

    def indexObject(self, *args, **kwargs):
        self.base_catalog.indexObject(*args, **kwargs)
        super(PeopleCatalog, self).indexObject(*args, **kwargs)

    def reindexObject(self, *args, **kwargs):
        self.base_catalog.reindexObject(*args, **kwargs)
        super(PeopleCatalog, self).reindexObject(*args, **kwargs)

    def unindexObject(self, *args, **kwargs):
        self.base_catalog.unindexObject(*args, **kwargs)
        super(PeopleCatalog, self).unindexObject(*args, **kwargs)

    def setup_lexicons(self):
        # setup the lexicons as some Plone-Catalog internal code depends on it
        # we wouldn't relly have to be so thorough as we don't actually want
        # to support full text searches on the people catalog, but setting
        # up the people catalog as close as possible to the portal catalog
        # ensures that there are no surprises
        lexicons = {
            'plone_lexicon': [
                ('Unicode Whitespace splitter', 'Word Splitter'),
                ('Unicode Ignoring Accents Case Normalizer',
                    'Case Normalizer'),
            ],
            'plaintext_lexicon': [
                ('HTML aware splitter', 'Word Splitter'),
                ('Case Normalizer', 'Case Normalizer'),
                ('Remove listed stop words only', 'Stop Words')
            ],
            'htmltext_lexicon': [
                ('HTML aware splitter', 'Word Splitter'),
                ('Case Normalizer', 'Case Normalizer'),
                ('Remove listed stop words only', 'Stop Words')
            ]
        }

        for lexicon, elements in lexicons.items():
            pipeline = []

            for element in elements:
                element = element_factory.instantiate(element[1], element[0])
                pipeline.append(element)

            plexicon = PLexicon(lexicon)
            plexicon._pipeline = pipeline
            self._setObject(lexicon, plexicon)

    def setup_indexes(self):
        # copy the indexes from the base catalog, so the code using the
        # people catalog doesn't have to know where each index/metadata-column
        # is stored exactly

        # only support known index types
        known_index_types = set((
            'BooleanIndex',
            'DateIndex',
            'DateRangeIndex',
            'ExtendedPathIndex',
            'FieldIndex',
            'GopipIndex',
            'KeywordIndex',
            'UUIDIndex',
            'ZCTextIndex',
        ))

        for index in self.base_catalog.index_objects():
            if index.meta_type not in known_index_types:
                log.warn('Unknown index type: {}'.format(index.meta_type))
                continue

            extra = Extra()

            if hasattr(index, 'lexicon_id'):
                extra.lexicon_id = index.lexicon_id

            if hasattr(index, '_index_type'):
                extra.index_type = index._index_type

            if hasattr(index, 'indexed_attrs'):
                extra.indexed_attrs = index.indexed_attrs

            if hasattr(index, 'since_field'):
                extra.since_field = index.since_field

            if hasattr(index, 'until_field'):
                extra.until_field = index.until_field

            self.addIndex(index.id, index.meta_type, extra=extra)

            if hasattr(index, 'index_naive_time_as_local'):
                new = self._catalog.getIndex(index.id)
                new.index_naive_time_as_local = index.index_naive_time_as_local

    def setup_metadata(self):
        # copy the metadata from the base catalog
        for name in self.base_catalog._catalog.names:
            self.addColumn(name)

    def searchResults(self, REQUEST=None, **kw):
        """Calls the catalog tool with avoiding using the 'effectiveRange'
        DateRangeIndex since our catalog has a not yet solved issue with it.
        (see https://github.com/seantis/seantis.people/issues/41)
        """
        kw = kw.copy()
        if 'effectiveRange' in kw:
            del kw['effectiveRange']

        return super(PeopleCatalog, self).searchResults(
            REQUEST, show_inactive=True, **kw
        )

    __call__ = searchResults


InitializeClass(PeopleCatalog)
