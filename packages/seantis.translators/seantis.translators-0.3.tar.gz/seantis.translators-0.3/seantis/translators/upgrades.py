from seantis.people.upgrades import upgrade_portal_type


def upgrade_translators_type_info(context):
    upgrade_portal_type(
        'seantis.translators.translator', 'seantis.translators', 'default'
    )
