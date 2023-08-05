from collections import namedtuple
from datetime import datetime, date

from five import grok
from zope.interface import Interface
from zope.security import checkPermission

from plone import api

from seantis.kantonsrat import _
from seantis.kantonsrat.browser.base import BaseView


class View(BaseView):
    """A numer of macros for use with seantis.people"""

    grok.context(Interface)
    grok.require('zope2.View')
    grok.name('seantis-kantonsrat-macros')

    template = grok.PageTemplateFile('templates/macros.pt')

    def __getitem__(self, key):
        return self.template._template.macros[key]

    def get_brain_from_relation(self, relation):
        if not relation:
            return None

        if relation.isBroken():
            return None

        catalog = api.portal.get_tool('portal_catalog')
        results = catalog(path={'query': relation.to_path})

        return results and results[0] or None

    def get_human_timespan(self, start, end):
        if not (start or end):
            return None

        today = datetime(*date.today().timetuple()[:3])

        start = start and datetime(start.year, start.month, start.day) or None
        end = end and datetime(end.year, end.month, end.day) or None

        if start and end:
            if today < start:
                return _(u'from ${start} until ${end}', mapping={
                    'start': api.portal.get_localized_time(start),
                    'end': api.portal.get_localized_time(end),
                })
            else:
                return _(u'since ${start} until ${end}', mapping={
                    'start': api.portal.get_localized_time(start),
                    'end': api.portal.get_localized_time(end),
                })

        if start:
            if today < start:
                return _(u'from ${start}', mapping={
                    'start': api.portal.get_localized_time(start)
                })
            else:
                return _(u'since ${start}', mapping={
                    'start': api.portal.get_localized_time(start)
                })

        else:
            return _(u'until ${end}', mapping={
                'end': api.portal.get_localized_time(end)
            })

    def as_simplified_structure(self, memberships):
        Member = namedtuple(
            'Member', [
                'id',
                'role',
                'person',
                'url',
                'note',
                'timespan',
                'replacement_for',
                'state',
                'edit',
                'publish',
                'retract'
            ]
        )

        states = {
            'private': _(u'Private'),
            'published': _(u'Published'),
        }

        for brain in memberships:
            membership = brain.getObject()
            person_brain = self.get_brain_from_relation(membership.person)

            # if the person is not published, None might be yielded
            if person_brain is None:
                continue

            replacement_for_brain = self.get_brain_from_relation(
                membership.replacement_for
            )

            replacement_for = replacement_for_brain and _(
                u'Replacement for ${name}', mapping={
                    'name': replacement_for_brain.Title.decode('utf-8')
                }
            ) or u''

            if checkPermission('cmf.ModifyPortalContent', membership):
                edit = membership.absolute_url() + '/edit'
                state = states.get(brain.review_state, brain.review_state)
                publish = brain.review_state == 'private' and ''.join((
                    brain.getURL(),
                    '/content_status_modify?workflow_action=publish'
                ))
                retract = brain.review_state == 'published' and ''.join((
                    brain.getURL(),
                    '/content_status_modify?workflow_action=retract'
                ))
            else:
                edit, state, publish, retract = None, None, None, None

            yield Member(
                membership.id,
                membership.role,
                person_brain.Title,
                person_brain.getURL(),
                membership.note,
                self.get_human_timespan(brain.start, brain.end),
                replacement_for,
                state,
                edit,
                publish,
                retract
            )
