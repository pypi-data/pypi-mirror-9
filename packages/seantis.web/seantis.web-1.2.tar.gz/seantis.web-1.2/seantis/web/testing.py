from plone.app.testing import PloneSandboxLayer
from plone.app.testing import applyProfile
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import IntegrationTesting
from plone.app.testing import FunctionalTesting

from plone.testing import z2

from zope.configuration import xmlconfig


class SeantiswebLayer(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        # Load ZCML
        import seantis.web
        xmlconfig.file(
            'configure.zcml',
            seantis.web,
            context=configurationContext
        )

        # Install products that use an old-style initialize() function
        #z2.installProduct(app, 'Products.PloneFormGen')

#    def tearDownZope(self, app):
#        # Uninstall products installed above
#        z2.uninstallProduct(app, 'Products.PloneFormGen')

    def setUpPloneSite(self, portal):
        applyProfile(portal, 'seantis.web:default')

SEANTIS_WEB_FIXTURE = SeantiswebLayer()
SEANTIS_WEB_INTEGRATION_TESTING = IntegrationTesting(
    bases=(SEANTIS_WEB_FIXTURE,),
    name="SeantiswebLayer:Integration"
)
SEANTIS_WEB_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(SEANTIS_WEB_FIXTURE, z2.ZSERVER_FIXTURE),
    name="SeantiswebLayer:Functional"
)
