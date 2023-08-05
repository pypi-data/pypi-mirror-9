import logging
log = logging.getLogger('seantis.kantonsrat')

import json
import urllib2

from uuid import uuid4 as new_uuid

from datetime import datetime
from itertools import chain

from zope.interface import implements
from plone.memoize import ram

from seantis.kantonsrat import settings
from seantis.kantonsrat.interfaces import IMotion, IMotionsProvider


class Motion(object):

    implements(IMotion)

    def __init__(self, title, url):
        self.title = title
        self.url = url


class GeschaeftsverzeichnisMotionsProvider(object):

    implements(IMotionsProvider)

    def __init__(self, url=None, cache_lifetime=None):
        self._url = url
        self._cache_lifetime = cache_lifetime
        self._last_fetch = None
        self._cache_version = None

    @property
    def url(self):
        if self._url is None:
            return self.get_url_from_settings()
        else:
            return self._url

    @property
    def cache_lifetime(self):
        if self._cache_lifetime is None:
            return settings.get('lifetime')
        else:
            return self._cache_lifetime

    @property
    def cache_version(self):
        last_fetch = (self._last_fetch or datetime.utcnow())
        cache_age = (datetime.utcnow() - last_fetch).total_seconds()

        if self._cache_version is None:
            self._cache_version = new_uuid().hex

        if cache_age > self.cache_lifetime:
            self._cache_version = new_uuid().hex

        return self._cache_version + self.url + str(self.cache_lifetime)

    def get_url_from_settings(self):
        base = (settings.get('geschaeftsverzeichnis') or '').strip()

        if not base:
            return ''

        if base.endswith('/api/geschaefte.json'):
            return base
        else:
            if not base.endswith('/'):
                base += '/'
            return base + 'api/geschaefte.json'

    def motions_by_entity(self, entity_uuid):
        motions = list(
            Motion(title=m['titel'], url=m['url'])
            for m in self.get_motions().get(entity_uuid, [])
        )

        return sorted(motions, key=lambda motion: motion.title)

    @ram.cache(lambda method, self: self.cache_version)
    def get_motions(self):
        return self.force_get_motions()

    def force_get_motions(self):

        external_motions_by_uuid = {}

        for external_motion in self.get_external_motions():
            uuids = chain(
                external_motion.get('eingereicht_von_refs', []),
                external_motion.get('kommissionen_refs', [])
            )
            normalize = lambda uid: uid.lower().replace('-', '')

            for uuid in (normalize(uid) for uid in uuids):
                if uuid in external_motions_by_uuid:
                    external_motions_by_uuid[uuid].append(external_motion)
                else:
                    external_motions_by_uuid[uuid] = [external_motion]

        return external_motions_by_uuid

    def open_url(self, timeout=5.0):
        if not self.url:
            return ''

        try:
            log.info('fetching motions from {}'.format(self.url))
            data = urllib2.urlopen(self.url, timeout=timeout).read()
        except:
            log.exception('could not fetch motions from {}'.format(self.url))
            data = ''

        return data.strip()

    def get_external_motions(self):
        # Set the timestamp before the fetch, if it fails we won't retry
        # until the timeout is up. This has the potential for missing data,
        # but it will make sure the website reacts fast at all times.
        self._last_fetch = datetime.utcnow()

        raw_data = self.open_url()
        if raw_data:
            try:
                return json.loads(raw_data)
            except:
                log.exception('Could not parse json')
                return []
        else:
            return []
