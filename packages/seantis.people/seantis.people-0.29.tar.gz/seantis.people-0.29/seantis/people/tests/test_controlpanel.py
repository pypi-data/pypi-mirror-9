from plone import api

from seantis.people import tests


class TestControlpanel(tests.IntegrationTestCase):

    @property
    def panel(self):
        with self.user('admin'):
            return api.content.get_view(
                name='seantis-people-controlpanel',
                context=api.portal.get(),
                request=self.request
            )

    def test_install_profiles(self):
        profiles = self.panel.available_profiles()
        map(self.panel.install_profile, profiles)
        
        ids = [p['id'] for p in self.panel.installed_profiles()]
        self.assertEqual(ids, [p['id'] for p in profiles])
        self.assertEqual(self.panel.available_profiles(), [])
        self.assertEqual(self.panel.upgradeable_profiles(), [])

    def test_included_profiles(self):
        # we should see the profiles included with seantis.people
        ids = [p['id'] for p in self.panel.available_profiles()]
        self.assertEqual(sorted(ids), [
            u'seantis.people:phz',
            u'seantis.people:standard'
        ])

        # they are not installed
        ids = [p['id'] for p in self.panel.installed_profiles()]
        self.assertEqual(ids, [])

        # and therefore not upgradable
        ids = [p['id'] for p in self.panel.upgradeable_profiles()]
        self.assertEqual(ids, [])
