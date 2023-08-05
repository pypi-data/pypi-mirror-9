from zope.schema import getFields

from seantis.kantonsrat import tests
from seantis.people.supermodel import security


class TestSchema(tests.IntegrationTestCase):

    def test_schema_load(self):
        from seantis.kantonsrat.types import IMember
        getFields(IMember)

    def test_private_fields(self):

        # ensure that the following fields are never defined as public
        really_private_fields = [
            'phone',
            'mobile',
            'fax',
            'private_address'
        ]

        from seantis.kantonsrat.types import IMember

        private_schema_fields = security.get_read_permissions(IMember)

        for field in really_private_fields:
            self.assertIn(field, private_schema_fields)
