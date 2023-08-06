__author__ = 'bdeggleston'

from rexpro.tests.base import BaseRexProTestCase
from nose.plugins.attrib import attr


@attr('unit')
class TestRexProSessionRequest(BaseRexProTestCase):

    def test_creating_session_works_properly(self):
        pass

    def test_defining_graph_works_properly(self):
        pass

    def test_defining_nonexistant_graph_returns_error(self):
        pass
