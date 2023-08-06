from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import IntegrationTesting
from plone.app.testing import applyProfile

from zope.configuration import xmlconfig


class CustomerLascatalinascr_Com(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE, )

    def setUpZope(self, app, configurationContext):
        # Load ZCML for this package
        import customer.lascatalinascr_com
        xmlconfig.file('configure.zcml',
                       customer.lascatalinascr_com,
                       context=configurationContext)

    def setUpPloneSite(self, portal):
        applyProfile(portal, 'customer.lascatalinascr_com:default')

CUSTOMER_LASCATALINASCR_COM_FIXTURE = CustomerLascatalinascr_Com()
CUSTOMER_LASCATALINASCR_COM_INTEGRATION_TESTING = \
    IntegrationTesting(bases=(CUSTOMER_LASCATALINASCR_COM_FIXTURE, ),
                       name='CustomerLascatalinascr_Com:Integration')
