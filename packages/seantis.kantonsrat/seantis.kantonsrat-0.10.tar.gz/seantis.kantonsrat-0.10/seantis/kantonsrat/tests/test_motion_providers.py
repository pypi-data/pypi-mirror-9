import json
from time import sleep

from seantis.kantonsrat import tests
from seantis.kantonsrat.motion_providers import (
    GeschaeftsverzeichnisMotionsProvider
)


class TestProvider(GeschaeftsverzeichnisMotionsProvider):

    called = 0
    json = u''

    def open_url(self):
        self.called += 1
        return self.json


class TestMotionsProvider(tests.IntegrationTestCase):

    def test_motions_caching(self):

        provider = TestProvider(url='', cache_lifetime=1.0)

        previous_version = provider.cache_version
        provider.get_motions()
        self.assertEqual(provider.called, 1)
        self.assertEqual(provider.cache_version, previous_version)

        previous_version = provider.cache_version
        provider.get_motions()
        self.assertEqual(provider.called, 1)
        self.assertEqual(provider.cache_version, previous_version)

        sleep(1.01)

        previous_version = provider.cache_version
        provider.get_motions()
        self.assertEqual(provider.called, 2)
        self.assertNotEqual(provider.cache_version, previous_version)

        # a changed url invalidates the cache
        previous_version = provider.cache_version
        provider._url = 'http://seantis.ch'
        provider.get_motions()
        self.assertEqual(provider.called, 3)
        self.assertNotEqual(provider.cache_version, previous_version)

        # as does a change in the timeout
        previous_version = provider.cache_version
        provider._cache_lifetime = 2.0
        provider.get_motions()
        self.assertEqual(provider.called, 4)
        self.assertNotEqual(provider.cache_version, previous_version)

    def test_get_motions(self):

        provider = TestProvider(url='', cache_lifetime=0)

        provider.json = u'asdfasdf{{{{'
        self.assertEqual(provider.get_external_motions(), [])
        self.assertEqual(provider.get_motions(), {})

        provider.json = u''
        self.assertEqual(provider.get_external_motions(), [])
        self.assertEqual(provider.get_motions(), {})

        provider.json = json.dumps([
            dict(
                id=1,
                titel='test',
                eingereicht_von_refs=['a', 'b'],
                kommissionen_refs=['c'],
                url='https://google.ch'
            )
        ])

        self.assertEqual(provider.get_external_motions(), json.loads(
            provider.json
        ))

        for ref in ('a', 'b', 'c'):
            motions = provider.motions_by_entity(ref)

            self.assertEqual(len(motions), 1)
            self.assertEqual(motions[0].title, 'test')
            self.assertEqual(motions[0].url, 'https://google.ch')
