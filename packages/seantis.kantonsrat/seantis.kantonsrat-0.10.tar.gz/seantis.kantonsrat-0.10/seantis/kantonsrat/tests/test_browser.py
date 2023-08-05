from freezegun import freeze_time
from datetime import date, timedelta

from plone import api

from seantis.plonetools import tools
from seantis.kantonsrat import tests


class TestBrowser(tests.FunctionalTestCase):

    def setUp(self):
        super(TestBrowser, self).setUp()
        self.baseurl = self.portal.absolute_url()
        self.admin_browser = browser = self.new_admin_browser()

        browser.open(self.baseurl + '/createObject?type_name=Folder')
        browser.getControl('Title').value = 'testfolder'
        browser.getControl('Save').click()

        self.folder_url = self.baseurl + '/testfolder'
        self.infolder = lambda url: self.folder_url + url

    def tearDown(self):
        self.admin_browser.open(self.infolder('/delete_confirmation'))
        self.admin_browser.getControl('Delete').click()

        super(TestBrowser, self).tearDown()

    def new_admin_browser(self):
        browser = self.new_browser()
        browser.login_admin()

        return browser

    def new_member_list(self, title):
        browser = self.new_admin_browser()

        browser.open(self.infolder('/++add++seantis.people.list'))
        browser.getControl(name='form.widgets.title').value = title
        browser.getControl('Save').click()

        return self.infolder('/{}'.format(title.lower()))

    def new_member(self, first_name, last_name, memberlist='members'):
        browser = self.new_admin_browser()

        browser.open(self.infolder('/{}'.format(memberlist)))
        self.assertIn('No people in the list.', browser.contents)

        browser.open(
            self.infolder(
                '/{}/++add++seantis.kantonsrat.member'.format(memberlist)
            )
        )
        browser.getControl('First Name').value = first_name
        browser.getControl('Last Name').value = last_name
        browser.getControl('Save').click()

        return self.infolder('/{}/{}-{}'.format(
            memberlist, last_name.lower(), first_name.lower()
        ))

    def test_add_member(self):
        browser = self.new_admin_browser()
        memberlist_url = self.new_member_list('members')

        browser.open(self.new_member('Frank', 'Underwood'))
        self.assertIn('Underwood Frank', browser.contents)

        browser.open(memberlist_url)
        self.assertIn('Frank', browser.contents)
        self.assertIn('Underwood', browser.contents)

    def test_organization_activation(self):
        browser = self.new_admin_browser()
        anonymous = self.new_browser()

        browser.open(self.infolder('/++add++seantis.kantonsrat.organization'))

        # by default, organizations are active
        browser.getControl('Title').value = u'NSA'
        browser.getControl('Description').value = u'Spying and stuff'
        browser.getControl('Save').click()

        browser.open(self.infolder(
            '/nsa/content_status_modify?workflow_action=publish'
        ))

        # at this point both manager and anonymous see the same
        browser.open(self.infolder('/organization_listing'))
        self.assertIn('<dt class="active">', browser.contents)
        self.assertNotIn('<dt class="inactive">', browser.contents)

        anonymous.open(self.infolder('/organization_listing'))
        self.assertIn('<dt class="active">', anonymous.contents)
        self.assertNotIn('<dt class="inactive">', anonymous.contents)

        # deactivating an organization tags it in the list and removes
        # it for anonymous users. It also won't show up in the navigation
        browser.open(self.infolder('/nsa/edit'))
        browser.set_date('start', date.today() + timedelta(days=1))
        browser.getControl('Save').click()

        # managers now see the inactive organizations
        browser.open(self.infolder('/organization_listing'))
        self.assertIn('<dt class="inactive">', browser.contents)
        self.assertNotIn('<dt class="active">', browser.contents)

        # while anonymous users do not
        anonymous.open(self.infolder('/organization_listing'))
        self.assertNotIn('<dt class="active">', anonymous.contents)
        self.assertNotIn('<dt class="inactive">', anonymous.contents)

        # unfortunately, using a date to trigger the state is not automatic.
        # a cronjob as to be used for this (which calls a view)
        last_week = date.today() - timedelta(days=7)
        last_year = date.today() - timedelta(days=365)
        with freeze_time(last_week):
            browser.open(self.infolder('/nsa/edit'))
            browser.set_date('start', last_year)
            browser.set_date('end', last_week)
            browser.getControl('Save').click()

        # the view is always up to date
        browser.open(self.infolder('/organization_listing'))
        self.assertIn('<dt class="inactive">', browser.contents)
        self.assertNotIn('<dt class="active">', browser.contents)

        # but the navigation isn't.. unfortunately I cannot get the
        # portlets to work here, so we have to peek into the brain
        # to see the actual state
        browser.open(self.infolder('/nsa/uuid'))
        uuid = browser.contents
        brain = tools.get_brain_by_object(api.content.get(UID=uuid))
        self.assertEqual(brain.exclude_from_nav, False)

        # trigger the state and this will change
        browser.open(self.infolder('/trigger-state'))

        brain = tools.get_brain_by_object(api.content.get(UID=uuid))
        self.assertEqual(brain.exclude_from_nav, True)
