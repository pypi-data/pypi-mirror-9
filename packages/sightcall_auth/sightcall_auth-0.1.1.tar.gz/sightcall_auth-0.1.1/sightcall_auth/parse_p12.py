#!/usr/bin/python
# -*- coding: utf-8 -*-
# coding:utf8

"""
Parse a p12 file.
"""

from OpenSSL.crypto import load_pkcs12, FILETYPE_PEM, dump_privatekey, dump_certificate
from os import path, makedirs
import argparse

import sightcall_auth.config

__all__ = ['parse_p12']


def parse_p12(p12_path, passphrase, directory):
    """
        :param p12_path: The path to the p12 file
        :param passphrase: The password to open the p12 file
        :param directory: The path where the p12 will be extracted
    """
    with open(p12_path, 'rb') as f:
        c = f.read()

    try:
        passphrase.decode(encoding='UTF-8')
    except:
        passphrase = passphrase.encode(encoding='UTF-8')

    p = load_pkcs12(c, passphrase)
    certificate = p.get_certificate()
    private_key = p.get_privatekey()

    if not path.exists(directory):
        makedirs(directory)

    private_key_file = path.join(directory, 'private_key.pem')
    with open(private_key_file, 'w') as pk:
        pk.write(dump_privatekey(FILETYPE_PEM, private_key).decode("utf-8"))

    cert_file = path.join(directory, 'cert.pem')
    with open(cert_file, 'w') as cert:
        cert.write(dump_certificate(FILETYPE_PEM, certificate).decode("utf-8"))

    print("p12 extracted!")
