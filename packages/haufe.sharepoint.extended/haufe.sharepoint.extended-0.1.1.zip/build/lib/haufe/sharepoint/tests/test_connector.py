import unittest

from haufe.sharepoint.connection import Connector

class ConnectorTests(unittest.TestCase):

    def testConnector(self):
        connector = Connector()
    
def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(ConnectorTests))
    return suite
