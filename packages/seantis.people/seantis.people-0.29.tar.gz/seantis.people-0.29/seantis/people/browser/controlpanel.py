import os, os.path

from five import grok
from plone import api
from Products.CMFPlone.interfaces import IPloneSiteRoot

from seantis.people.browser.base import BaseView
from seantis.people.interfaces import IPerson


class ControlPanel(BaseView):

    permission = 'cmf.ManagePortal'
    grok.require(permission)
    grok.context(IPloneSiteRoot)
    grok.name('seantis-people-controlpanel')

    template = grok.PageTemplateFile('templates/controlpanel.pt')

    @property
    def setup(self):
        return api.portal.get_tool('portal_setup')

    @property
    def installer(self):
        return api.portal.get_tool('portal_quickinstaller')

    def update(self):
        if 'upgrade-profile' in self.request:
            profile = self.get_profile_by_id(self.request['upgrade-profile'])

            if profile:
                self.upgrade_profile(profile)

        if 'install-profile' in self.request:
            profile = self.get_profile_by_id(self.request['install-profile'])

            if profile:
                self.install_profile(profile)

    def upgrade_profile(self, profile):
        # copied from Products.CMFCore.QuickInstallerTool
        for upgrade in self.setup.listUpgrades(profile['id']):
            if not type(upgrade) is list:
                upgrade = [upgrade]
            for upgradestep in upgrade:
                step = upgradestep['step']
                step.doStep(self.setup)
        version = str(profile['version'])
        if version == 'latest':
            version = self.installer.getLatestUpgradeStep(profile['id'])
        self.set_last_version(profile, version)

    def install_profile(self, profile):
        pid = 'profile-{}'.format(profile['id'])
        self.setup.runAllImportStepsFromProfile(pid)
        self.set_last_version(profile)

    def get_profile_by_id(self, profile_id):
        profiles = self.relevant_profiles()

        for profile in profiles:
            if profile['id'] == profile_id:
                return profile

        return None

    def get_last_version(self, profile):
        version = self.setup.getLastVersionForProfile(profile['id'])

        if version == 'unknown':
            return None
        else:
            return version[0]

    def set_last_version(self, profile, version=None):
        version = version or profile['version']

        self.setup.setLastVersionForProfile(profile['id'], version)

    def relevant_profiles(self):
        return [
            p for p in self.setup.listProfileInfo() if self.has_people_type(p)
        ]

    def has_people_type(self, profile):
        try:
            types = os.path.join(profile['path'], 'types')
            files = os.listdir(types)
        except OSError:
            return False

        for f in files:
            try:
                with open(os.path.join(types, f), 'r') as typeinfo:
                    for line in typeinfo:
                        if IPerson.__identifier__ in line:
                            return True
            except IOError:
                continue

        return False

    def is_installed_profile(self, profile):
        return self.get_last_version(profile) is not None

    def is_latest_profile(self, profile):
        return self.get_last_version(profile) == profile['version']

    def available_profiles(self):
        available = lambda p: not self.is_installed_profile(p)
        return [p for p in self.relevant_profiles() if available(p)]

    def installed_profiles(self):
        installed = lambda p: self.is_installed_profile(p)
        return [p for p in self.relevant_profiles() if installed(p)]

    def upgradeable_profiles(self):
        upgradeable = lambda p: not self.is_latest_profile(p)
        return [p for p in self.installed_profiles() if upgradeable(p)]
