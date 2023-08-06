#!/usr/bin/python
# -*- coding: utf-8 -*-
# coding:utf8

"""
Send a SSL request to the SightCall authentification API, with the key
and certificate extracted from a p12 file.
"""

from os import path, makedirs
import json

import requests

from sightcall_auth.config import directory as default_cert_dir

__all__ = ['Auth']


class ServerError(Exception):
    pass


class Auth():

    """
        :param client_id: The client ID of your provider
        :param client_secret: The client secret of your provider
        :param url: The url where the request will be sent
        :param auth_ca: The path to the SightCall certificate file
        :return: A token ready ot be used
        :rtype: str
    """
    client_id = None
    client_secret = None
    url = None
    directory = None
    auth_ca = None

    def __init__(self, client_id, client_secret, url, auth_ca,
                 cert_directory=default_cert_dir):
        self.client_id = client_id
        self.client_secret = client_secret
        self.url = url
        self.directory = cert_directory
        self.auth_ca = auth_ca

    def connect(self, uid):
        url_params = "?client_id={0}&client_secret={1}&uid={2}"\
            .format(self.client_id, self.client_secret, uid)
        url = path.join(self.url,  url_params)

        key = path.join(self.directory, 'private_key.pem')
        cert = path.join(self.directory, 'cert.pem')

        r = requests.get(url, cert=(cert, key), verify=self.auth_ca)
        try:
            data = r.json()
            return data['token']
        except ValueError:
            raise ServerError(
                "Server returned a value that was not JSON: {0}"
                .format(r.text)
            )
