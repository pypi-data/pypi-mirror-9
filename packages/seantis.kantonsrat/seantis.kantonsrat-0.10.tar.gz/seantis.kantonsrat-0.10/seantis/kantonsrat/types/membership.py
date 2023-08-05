from five import grok

from zope import schema
from zope.interface import invariant, Invalid
from zope.schema.interfaces import IContextSourceBinder
from z3c.relationfield.schema import RelationChoice

from plone.formwidget.contenttree import ObjPathSourceBinder
from plone.uuid.interfaces import IUUID

from seantis.people.interfaces import IMembership as IPeopleMembership
from seantis.people.content import Membership as PeopleMembership
from seantis.kantonsrat.types import IOrganization
from seantis.kantonsrat import _


class Membership(PeopleMembership):

    @property
    def replacement_for_uuid(self):
        if self.replacement_for and not self.replacement_for.isBroken():
            try:
                if isinstance(self.replacement_for, Membership):
                    return IUUID(self.replacement_for)
                else:
                    return IUUID(self.replacement_for.to_object)
            except AttributeError:
                # Zope swallows AttributeErrors like there's no tomorrow
                assert False, "replacement_for uuid could not be determined"
        else:
            return None


@grok.provider(IContextSourceBinder)
def available_memberships(context):

    if IOrganization.providedBy(context):
        path = {
            'query': '/'.join(context.getPhysicalPath()),
            'depth': '1'
        }
    else:
        path = {
            'query': '/'.join(context.aq_inner.aq_parent.getPhysicalPath()),
            'depth': '1'
        }

    query = {
        'portal_type': 'seantis.kantonsrat.membership',
        'path': path
    }

    return ObjPathSourceBinder(navigation_tree_query=query).__call__(context)


class IMembership(IPeopleMembership):

    start = schema.Date(
        title=_(u"Start of membership"),
        required=False
    )

    end = schema.Date(
        title=_(u"End of membership"),
        required=False
    )

    replacement_for = RelationChoice(
        title=_(u"Replacement for"),
        description=_(u"The membership which this membership replaces"),
        source=available_memberships,
        required=False
    )

    @invariant
    def has_valid_daterange(Membership):
        if Membership.start is None:
            return

        if Membership.end is None:
            return

        if Membership.start > Membership.end:
            raise Invalid(_(u"The membership can't end before it starts"))
