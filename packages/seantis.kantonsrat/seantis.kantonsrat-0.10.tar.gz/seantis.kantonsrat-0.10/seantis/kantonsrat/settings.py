# -*- coding: utf-8 -*-

from zope.interface import Interface
from zope import schema

from plone import api
from plone.app.registry.browser.controlpanel import RegistryEditForm
from plone.app.registry.browser.controlpanel import ControlPanelFormWrapper
from plone.z3cform import layout

from seantis.kantonsrat import _


class ISeantisKantonsratSettings(Interface):

    geschaeftsverzeichnis = schema.TextLine(
        title=_(u"URL to the Geschäftsverzeichnis"),
        description=_(
            u"Used to show data from the Geschäftsverzeichnis on "
            u"the member and organisation pages. Leave empty if "
            u"there's no such connection."
        ),
        required=False
    )

    lifetime = schema.Int(
        title=_(u"Lifetime of Geschäftsverzeichnis cache"),
        description=_(
            u"The number of seconds a request to the Geschäftsverzeichnis "
            u"should be kept in the local cache. "
        ),
        required=False,
        default=3600
    )

    svg_logo = schema.Text(
        title=_(u"SVG Logo for Report"),
        description=_(
            u"SVG Logo (in XMl) which should be used by the Report."
        ),
        required=False,
        default=u''
    )


def get(name):
    prefix = ISeantisKantonsratSettings.__identifier__
    return api.portal.get_registry_record('.'.join((prefix, name)))


def set(name, value):
    prefix = ISeantisKantonsratSettings.__identifier__
    return api.portal.set_registry_record('.'.join((prefix, name)), value)


class SeantisKantonsratSettingsPanelForm(RegistryEditForm):
    schema = ISeantisKantonsratSettings
    label = _(u"Seantis Kantonsrat Settings")


SeantisKantonsratControlPanelView = layout.wrap_form(
    SeantisKantonsratSettingsPanelForm, ControlPanelFormWrapper
)
