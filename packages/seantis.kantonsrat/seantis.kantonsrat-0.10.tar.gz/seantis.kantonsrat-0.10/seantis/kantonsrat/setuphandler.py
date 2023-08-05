from seantis.plonetools import setuphandlers

indexes = [
    ('organization_type', 'FieldIndex'),
    ('organization_start', 'FieldIndex'),
    ('organization_end', 'FieldIndex')
]


def add_catalog_indexes(context, logger=None):
    setuphandlers.add_catalog_indexes(
        'seantis.kantonsrat', indexes, context, logger
    )


def import_indexes(context):
    setuphandlers.import_indexes(
        'seantis.kantonsrat', indexes, context
    )
