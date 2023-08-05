from datetime import date
from freezegun import freeze_time
from plone import api
from seantis.kantonsrat import tests


class TestOrganization(tests.IntegrationTestCase):

    def test_membership_by_state(self):
        self.login('admin')

        container = self.new_temporary_folder()

        organization = api.content.create(
            container=container,
            type='seantis.kantonsrat.organization',
            title=u'White House'
        )

        presidents = api.content.create(
            container=container,
            type='seantis.people.list',
            title=u'Presidents'
        )

        bush = api.content.create(
            container=presidents,
            type='seantis.kantonsrat.member',
            title=u'George W. Bush',
            firstname='George W.',
            lastname='Bush',
        )

        api.content.create(
            container=organization,
            type='seantis.kantonsrat.membership',
            title=u'43rds First Term',
            role=u'President',
            person=bush,
            start=date(2001, 1, 20),
            end=date(2005, 1, 19)
        )

        api.content.create(
            container=organization,
            type='seantis.kantonsrat.membership',
            title=u'43rds Second Term',
            role=u'President',
            person=bush,
            start=date(2005, 1, 20),
            end=date(2009, 1, 19)
        )

        memberships = lambda state: organization.memberships(state=state)

        with freeze_time(date(2001, 1, 19)):
            self.assertEqual(len(memberships(state='all')), 2)
            self.assertEqual(len(memberships(state='past')), 0)
            self.assertEqual(len(memberships(state='present')), 0)
            self.assertEqual(len(memberships(state='future')), 2)

        with freeze_time(date(2001, 1, 20)):
            self.assertEqual(len(memberships(state='all')), 2)
            self.assertEqual(len(memberships(state='past')), 0)
            self.assertEqual(len(memberships(state='present')), 1)
            self.assertEqual(len(memberships(state='future')), 1)

        with freeze_time(date(2005, 1, 19)):
            self.assertEqual(len(memberships(state='all')), 2)
            self.assertEqual(len(memberships(state='past')), 0)
            self.assertEqual(len(memberships(state='present')), 1)
            self.assertEqual(len(memberships(state='future')), 1)

        with freeze_time(date(2005, 1, 20)):
            self.assertEqual(len(memberships(state='all')), 2)
            self.assertEqual(len(memberships(state='past')), 1)
            self.assertEqual(len(memberships(state='present')), 1)
            self.assertEqual(len(memberships(state='future')), 0)

        with freeze_time(date(2009, 1, 19)):
            self.assertEqual(len(memberships(state='all')), 2)
            self.assertEqual(len(memberships(state='past')), 1)
            self.assertEqual(len(memberships(state='present')), 1)
            self.assertEqual(len(memberships(state='future')), 0)

        with freeze_time(date(2009, 1, 20)):
            self.assertEqual(len(memberships(state='all')), 2)
            self.assertEqual(len(memberships(state='past')), 2)
            self.assertEqual(len(memberships(state='present')), 0)
            self.assertEqual(len(memberships(state='future')), 0)
