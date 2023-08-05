from zope.component import getUtility
from plone import api
from plone.registry.interfaces import IRegistry
from collective.js.jqueryui.interfaces import IJQueryUIPlugins

from seantis.people.upgrades import (
    run_import_step_from_profile,
    upgrade_portal_type
)
from seantis.kantonsrat.types import IOrganization


def remove_faulty_type_name(context):
    run_import_step_from_profile('typeinfo', 'seantis.kantonsrat', 'default')
    api.portal.get_tool('portal_catalog').clearFindAndRebuild()


def upgrade_type_info(context):
    upgrade_portal_type(
        'seantis.kantonsrat.member', 'seantis.kantonsrat', 'default'
    )


def upgrade_membership_title(context):
    from seantis.people.upgrades import upgrade_membership_title as upgrade
    upgrade(context)


def move_to_new_membership_type(context):
    catalog = api.portal.get_tool('portal_catalog')
    memberships = [m.getObject() for m in catalog.unrestrictedSearchResults(
        portal_type='seantis.people.membership'
    )]

    for membership in memberships:
        parent = membership.aq_inner.aq_parent

        if not IOrganization.providedBy(parent):
            continue

        new_membership = api.content.create(
            type='seantis.kantonsrat.membership',
            container=parent,
            id=membership.id + '-new',
            title=membership.title,
            role=membership.role,
            note=membership.note,
            person=membership.person,
        )

        old_id = membership.id
        new_id = new_membership.id

        api.content.delete(obj=membership)
        parent.manage_renameObject(new_id, old_id)

        parent.reindexObject()
        new_membership.reindexObject()


def add_new_membership_metadata(context):
    catalog = api.portal.get_tool('portal_catalog')
    memberships = [m.getObject() for m in catalog.unrestrictedSearchResults(
        portal_type='seantis.kantonsrat.membership'
    )]

    for membership in memberships:
        membership.reindexObject()


def install_custom_controlpanel(context):
    run_import_step_from_profile(
        'plone.app.registry', 'seantis.kantonsrat', 'default'
    )
    run_import_step_from_profile(
        'controlpanel', 'seantis.kantonsrat', 'default'
    )


def update_javascript(context):
    run_import_step_from_profile(
        'jsregistry', 'seantis.kantonsrat', 'default'
    )


def install_jquery_ui(context):
    setup = api.portal.get_tool('portal_setup')
    registry = getUtility(IRegistry)

    try:
        proxy = registry.forInterface(IJQueryUIPlugins)
        already_installed = True
    except KeyError:
        already_installed = False

    setup.runAllImportStepsFromProfile(
        'profile-collective.js.jqueryui:default'
    )

    # There's currently a conflict between plone's autocomplete and jQuery UIs
    # autocomplete. For now it can be worked arouned by disabling jQuery UIs
    # autocomplete, until the bug is fixed:
    # https://github.com/plone/plone.formwidget.autocomplete/issues/5
    #
    # We only do this if we're the ones installing jQuery UI at this point.
    if not already_installed:
        proxy = registry.forInterface(IJQueryUIPlugins)
        setattr(proxy, 'ui_autocomplete', False)


def update_settings(context):
    run_import_step_from_profile(
        'plone.app.registry', 'seantis.kantonsrat', 'default'
    )


def make_email_private(context):
    upgrade_type_info(context)

    catalog = api.portal.get_tool('portal_catalog')
    memberships = [m.getObject() for m in catalog.unrestrictedSearchResults(
        portal_type='seantis.kantonsrat.membership'
    )]

    for membership in memberships:
        membership.reindexObject()
