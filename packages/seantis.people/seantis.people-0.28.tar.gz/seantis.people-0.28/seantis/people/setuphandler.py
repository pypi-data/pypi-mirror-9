from seantis.people import catalog_id
from seantis.plonetools import setuphandlers

indexes = [
    ('first_letter', 'FieldIndex'),
    ('membership_person', 'FieldIndex'),
    ('is_active_person', 'FieldIndex')
]


def add_catalog_indexes(context, logger=None):
    # these indexes are not dynamic and need to be available in both catalogs
    # -> only the dynamic indexes created by the supermodel are only bound
    # to the people's catalog
    for catalog in ('portal_catalog', catalog_id):
        setuphandlers.add_catalog_indexes(
            'seantis.people', indexes, context, logger, catalog
        )


def import_indexes(context):
    # see above..
    for catalog in ('portal_catalog', catalog_id):
        setuphandlers.import_indexes(
            'seantis.people', indexes, context, catalog
        )
