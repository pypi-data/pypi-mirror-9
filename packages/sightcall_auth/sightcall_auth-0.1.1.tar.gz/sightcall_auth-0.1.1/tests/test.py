import unittest
import shutil
import os
import responses
import requests

from ..sightcall_auth.request import Auth
from ..sightcall_auth.request import ServerError
from ..sightcall_auth.parse_p12 import parse_p12
from ..sightcall_auth import config

dirname = os.path.dirname(os.path.abspath(__file__))


client_id = "8ce032d3a4a06c0c59eeb2393adcdb"
client_secret = "4204a68d25df3dc60653c3e9b28687"
url = "https://auth-ppr.rtccloud.net/auth/"
ca = os.path.join(dirname, '../../authCA.crt')
p12_path = os.path.join(dirname, '../../client.p12')


class TestConnectError(unittest.TestCase):

    @responses.activate
    def test_my_api(self):
        responses.add(responses.GET, 'https://auth-ppr.rtccloud.net/auth/',
                      body='This is not json', status=200,
                      content_type='plain/text')

        def helper():
            token = Auth(
                client_id,
                client_secret,
                url,
                ca,
                config.directory
            ).connect('toto')

        self.assertRaises(ServerError, helper)


# @httpretty.activate
#     def test_error(self):
#         httpretty.enable()
#         httpretty.register_uri(httpretty.GET, "http://yipit.com/",
#                                body="Find the best daily deals")

#         response = requests.get('http://yipit.com')
#         self.assertEqual(response.text, "Find the best daily deals")
#         httpretty.disable()


class TestConnect(unittest.TestCase):

    def test_default(self):
        token = Auth(client_id, client_secret, url, ca).connect('toto')
        self.assertTrue(isinstance(token, str))

    def test_with_directory(self):
        client_id = "8ce032d3a4a06c0c59eeb2393adcdb"
        client_secret = "4204a68d25df3dc60653c3e9b28687"
        url = "https://auth-ppr.rtccloud.net/auth/"
        token = Auth(
            client_id,
            client_secret,
            url,
            ca,
            config.directory
        ).connect('toto')
        self.assertTrue(isinstance(token, str))


class TestExtract(unittest.TestCase):
    directory = "/tmp/sightcall/auth/test"

    def setup(self):
        shutil.rmtree(self.directory)

    def tearDown(self):
        shutil.rmtree(self.directory)

    def test_extract(self):
        passphrase = "XnyexbUF"
        parse_p12(p12_path, passphrase, self.directory)
        self.assertTrue(os.path.isfile(
            os.path.join(self.directory, 'private_key.pem')
        ))


if __name__ == '__main__':
    unittest.main()
