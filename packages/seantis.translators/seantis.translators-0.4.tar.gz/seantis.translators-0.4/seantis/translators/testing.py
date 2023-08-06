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

        # Set up sessioning objects
        app.REQUEST['SESSION'] = self.Session()
        ZopeTestCase.utils.setupCoreSessions(app)

        import seantis.plonetools
        self.loadZCML(package=seantis.plonetools)

        import seantis.translators
        self.loadZCML(package=seantis.translators)

        xmlconfig.file(
            'configure.zcml',
            seantis.translators,
            context=configurationContext
        )

    def setUpPloneSite(self, portal):
        quickInstallProduct(portal, 'seantis.translators')
        applyProfile(portal, 'seantis.translators:default')

    def tearDownZope(self, app):
        z2.uninstallProduct(app, 'seantis.translators')


Layer = TestLayer()


INTEGRATION_TESTING = IntegrationTesting(
    bases=(Layer, ),
    name="Testfixture:Integration"
)

FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(Layer, ),
    name="Testfixture:Functional"
)
