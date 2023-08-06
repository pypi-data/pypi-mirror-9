#!/usr/bin/python
# -*- coding: utf-8 -*-
# coding:utf8


from OpenSSL.crypto import load_pkcs12, FILETYPE_PEM, dump_privatekey, dump_certificate
from os import path, makedirs
import argparse

import sightcall_auth.parse_p12 as parse_p12
import sightcall_auth.config as config

__all__ = ['extract']

parser = argparse.ArgumentParser(description='Extract a p12 file.')
parser.add_argument(
    '--p12_path',
    type=str,
    help='The path to the p12 file.',
    default='client.p12'
)
parser.add_argument(
    'passphrase', type=str, help='The passphrase of the p12 file.')
args = parser.parse_args()



def extract():
    parse_p12(args.p12_path, args.passphrase, config.directory)