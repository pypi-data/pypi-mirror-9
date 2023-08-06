from plone import api
from seantis.people.upgrades import upgrade_portal_type


def upgrade_translators_type_info(context):
    upgrade_portal_type(
        'seantis.translators.translator', 'seantis.translators', 'default'
    )


def enable_referenceablebehavior(context):
    catalog = api.portal.get_tool('portal_catalog')
    uid_catalog = api.portal.get_tool('uid_catalog')
    types = api.portal.get_tool('portal_types')
    portal = api.portal.get()

    type_name = 'seantis.translators.translator'
    types[type_name].behaviors += (
        'plone.app.referenceablebehavior.referenceable.IReferenceable',)

    for brain in catalog.unrestrictedSearchResults(portal_type=type_name):
        obj = portal.unrestrictedTraverse(brain.getPath())
        uid_catalog.catalog_object(obj, brain.getPath())
