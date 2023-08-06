#!/usr/bin/env python
# ***** BEGIN LICENSE BLOCK *****
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.
# ***** END LICENSE BLOCK *****

#
# TODO:
#
#  - Add a --verbose option with more output
#

from __future__ import print_function

import ConfigParser
import sys

from optparse import OptionParser

from websigning.credentials.jwsplat import JWSplatCredentials


def check_receipt_keys(certfile, keyfile, check_expiration=False):
    """
    Check receipt signing keys to be sure they're operationally correct.

    check_expiration should be the number of seconds until the key expires
        e.g., 86400 would check that the key is fresh at least until tomorrow
        at the same time.
    """
    try:
        JWSplatCredentials(keyfile, certfile,
                           check_cert_signature=True,
                           check_expiration=check_expiration)
    except Exception, e:
        print("ERROR: ", str(e), file=sys.stderr)
        sys.exit(1)


def check_receipt_keys_from_config(path, check_expiration=False):
    config = ConfigParser.ConfigParser()

    try:
        config.read(path)
    except ConfigParser.Error, e:
        print("INI file doesn't seem to be parseable by ConfigParser: {0}"
              .format(e), file=sys.stderr)
        sys.exit(1)

    try:
        certfile = config.get('trunion', 'certfile')
        keyfile = config.get('trunion', 'keyfile')
    except ConfigParser.NoOptionError:
        print("keyfile or certfile options are missing from the trunion "
              "section of the config.", file=sys.stderr)
        sys.exit(1)

    check_receipt_keys(certfile, keyfile, check_expiration)


def check_keys_main():
    parser = OptionParser(usage='verify_keys.py [-e expiry] [cert] [key]')
    parser.add_option("-e", "--expires", type='int',
                      help='check that key is valid until now + expiry')

    (options, args) = parser.parse_args()

    check_receipt_keys(args[0], args[1], check_expiration=options.expires)
