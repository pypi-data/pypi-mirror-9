#!/usr/bin/env python
import sys
from jwkest.jws import JWS
from jwkest.jwk import SYMKey

__author__ = 'rohe0002'

import argparse

from jwkest import unpack


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-r', dest="rsa_file",
                        help="File containing a RSA key")
    parser.add_argument('-p', dest="rsa_pub_file",
                        help="File containing a public RSA key")
    parser.add_argument('-k', dest="hmac_key",
                        help="If using a HMAC algorithm this is the key")
    parser.add_argument("message", nargs="?",
                        help="The message to verify signature on")

    args = parser.parse_args()

    keys = []
    if args.hmac_key:
        keys = [SYMKey(key=args.hmac_key)]

    # if args.rsa_file:
    #     keys = {"rsa": [rsa_load(args.rsa_file)]}
    # elif args.x509_file:
    #     keys = {"rsa": [x509_rsa_loads(open(args.x509_file).read())]}
    # elif args.rsa_pub_file:
    #     keys = {"rsa": [rsa_pub_load(args.rsa_pub_file)]}

    if args.message == "-":
        message = sys.stdin.read()
    else:
        message = args.message

    jws = JWS()

    if keys:
        print jws.verify_compact(args.message, keys)
    else:
        print unpack(message)[1]
