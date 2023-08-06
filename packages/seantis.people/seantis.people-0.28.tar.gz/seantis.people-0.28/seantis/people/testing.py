from plone.app.testing import PloneSandboxLayer
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import IntegrationTesting
from plone.app.testing import FunctionalTesting
from plone.app.testing import applyProfile
from plone.app.testing import quickInstallProduct

from plone.testing import z2
from Testing import ZopeTestCase
from zope.configuration import xmlconfig


class TestLayer(PloneSandboxLayer):

    default_bases = (PLONE_FIXTURE,)

    class Session(dict):
        def set(self, key, value):
            self[key] = value

    def setUpZope(self, app, configurationContext):

        # register the people schemahandler before anything else to ensure
        # that the seantis.people.types.* interfaces are loaded correctly

        # if not, the xml base of those interfaces is not parsed correctly
        from seantis.people.supermodel.schemahandler import (
            PeopleSchemaMetaHandler
        )
        PeopleSchemaMetaHandler.register_utility()

        # Set up sessioning objects
        app.REQUEST['SESSION'] = self.Session()
        ZopeTestCase.utils.setupCoreSessions(app)

        import seantis.plonetools
        self.loadZCML(package=seantis.plonetools)

        import seantis.people
        self.loadZCML(package=seantis.people)

        xmlconfig.file(
            'configure.zcml',
            seantis.people,
            context=configurationContext
        )

    def setUpPloneSite(self, portal):
        quickInstallProduct(portal, 'seantis.people')
        applyProfile(portal, 'seantis.people:default')

    def tearDownZope(self, app):
        z2.uninstallProduct(app, 'seantis.people')


class BrowserTestLayer(TestLayer):

    def setUpPloneSite(self, portal):
        # install the standard people type for the browser tests
        super(BrowserTestLayer, self).setUpPloneSite(portal)
        applyProfile(portal, 'seantis.people:standard')


INTEGRATION_TESTING = IntegrationTesting(
    bases=(TestLayer(), ),
    name="Testfixture:Integration"
)

FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(BrowserTestLayer(), ),
    name="Testfixture:Functional"
)
