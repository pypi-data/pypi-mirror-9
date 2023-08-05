import base64
import json
import argparse
import os
from Crypto.PublicKey import RSA
from jwkest.jwk import long_to_base64

__author__ = 'rolandh'

# usage: java -jar json-web-key-generator.jar -t <keyType> -s <keySize> [-u
#
# <keyUsage> -a <algorithm> -i <keyId> -p]
# -a <arg>   Algorithm.
# -i <arg>   Key ID (optional)
# -p         Display public key separately
# -s <arg>   Key Size in bits, must be an integer, generally divisible by 8
# -t <arg>   Key Type, one of: RSA, oct
# -u <arg>   Usage, one of: enc, sig. Defaults to sig


def create_rsa_key(alg, keyid, keysize, usage=""):
    #Seed the random number generator with 1024 random bytes (8192 bits)
    key = RSA.generate(keysize)

    res = {
        "kty": "RSA",
        "n": long_to_base64(key.n),
        "e": long_to_base64(key.e),
    }
    if alg:
        assert len(alg) == 5
        assert alg.startswith("RS")
        res["alg"] = alg
    if keyid:
        res["kid"] = keyid
    if usage:
        res["use"] = usage
    return "Key:\n%s" % json.dumps(res)


def create_hmac_key(alg, keyid, keysize, usage):
    key = os.urandom(int(keysize) / 8)
    res = {
        "kty": "oct",
        "k": base64.urlsafe_b64encode(key),
    }
    if alg:
        assert len(alg) == 5
        assert alg.startswith("HS")
        res["alg"] = alg
    if keyid:
        res["kid"] = keyid
    if usage:
        res["use"] = usage
    return "Key:\n%s" % json.dumps(res)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-a', dest="alg", help="Algorithm")
    parser.add_argument('-i', dest="keyid", help="Key ID (optional)")
    parser.add_argument('-p', dest="disp", action='store_true',
                        help="Display public key separately")
    parser.add_argument('-s', dest="keysize",
                        help="Key Size in bits, must be an integer, generally "
                             "divisible by 8")
    parser.add_argument('-t', dest="keytype",
                        help="Key Type, one of: RSA, oct")
    parser.add_argument('-u', dest="usage",
                        help="Usage, one of: enc, sig. Defaults to sig")

    args = parser.parse_args()

    if args.keytype:
        if args.keytype.upper() == "RSA":
            print create_rsa_key(args.alg, args.keyid, args.keysize, args.usage)
        elif args.keytype.upper() == "OCT":
            print create_hmac_key(args.alg, args.keyid, args.keysize,
                                  args.usage)
        else:
            print "Unsupported key type"
    else:
        print "You have to specify key type"