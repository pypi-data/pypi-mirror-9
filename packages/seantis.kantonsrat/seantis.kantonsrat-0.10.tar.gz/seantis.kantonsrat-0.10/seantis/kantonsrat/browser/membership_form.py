from five import grok
from z3c.form import field
from plone.directives.dexterity import AddForm

from seantis.plonetools.browser import BaseGroup
from seantis.kantonsrat.types.membership import IMembership
from seantis.kantonsrat import _
from seantis.kantonsrat.browser.base import BaseForm


class GeneralGroup(BaseGroup):
    label = _(u'General')

    group_fields = [
        [IMembership, ['role', 'start', 'end', 'note']]
    ]


class AdvancedGroup(BaseGroup):
    label = _(u'Advanced')

    group_fields = [
        [IMembership, ['person', 'replacement_for']]
    ]

    def update_fields(self):
        self.fields['person'].field.description = _(
            u"Don't change this value if a new members replaces this member. "
            u"Instead, change this members role and add a new member with the "
            u"new role. Otherwise the history of this organization won't be "
            u"correct anymore. "
        )


class MembershipBaseForm(BaseForm):

    grok.baseclass()

    @property
    def organization(self):
        raise NotImplementedError

    def before_save(self, data):
        if not data.get('replacement_for'):
            return

        replacement_org = data['replacement_for']
        replacement_org = replacement_org.aq_inner.aq_parent.getPhysicalPath()

        current_org = self.organization.getPhysicalPath()

        if replacement_org != current_org:
            self.raise_action_error(
                _(u'The replaced membership belongs to another organization')
            )


class LimitedMembershipAddForm(AddForm, MembershipBaseForm):
    grok.name('seantis.kantonsrat.membership')

    grok.context(IMembership)
    grok.require('cmf.AddPortalContent')

    fields = field.Fields(IMembership).select(
        'person', 'role', 'start', 'end', 'note', 'replacement_for'
    )

    @property
    def organization(self):
        return self.context


class LimitedMembershipEditForm(MembershipBaseForm):
    """ Provides an edit form for memberships in seantis.kantonsrat. Said
    form does not offer all fields. It namely removes the ability to change
    the referenced person.

    """
    grok.name('edit')

    grok.context(IMembership)
    grok.require('cmf.ModifyPortalContent')

    groups = (GeneralGroup, AdvancedGroup)

    enable_form_tabbing = True
    ignoreContext = False

    @property
    def organization(self):
        return self.context.aq_inner.aq_parent

    @property
    def label(self):
        organization = self.context.aq_inner.aq_parent.Title().decode('utf-8')
        person = self.context.person.to_object.title
        return u' - '.join((organization, person))

    @property
    def success_url(self):
        return self.context.aq_inner.aq_parent.absolute_url()

    @property
    def cancel_url(self):
        return self.context.aq_inner.aq_parent.absolute_url()
