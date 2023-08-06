import unittest
from unittest.mock import patch

from ..client import Client
from ..exceptions import BadCredentials


class TestClient(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_connect_pass(self):
        with patch.object(Client, '_Client__get_credentials', return_value=True) as mock_method:
            c = Client(
                "http://mydomain.com",
                "http://mystreamingdomain.com",
                "my_account",
                "my_token"
            )
    def test_connect_fail(self):
        with patch.object(Client, '_Client__get_credentials', return_value=False) as mock_method:
            with self.assertRaises(BadCredentials):
                c = Client(
                    "http://mydomain.com",
                    "http://mystreamingdomain.com",
                    "my_account",
                    "my_token"
                )