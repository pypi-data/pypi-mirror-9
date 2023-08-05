import argparse
import subprocess

__author__ = 'roland'

# sign
# openssl rsautl -sign -in file -inkey key.pem -out sig
# verify
# openssl rsautl -verify -in sig -inkey key.pem

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', dest="sign", action='store_true')
    parser.add_argument('-v', dest="verify", action='store_true')
    parser.add_argument('-f', dest="msg_file",
                        help="File containing a message")
    parser.add_argument('-r', dest="rsa_file",
                        help="File containing a RSA key")
    parser.add_argument('-a', dest="alg",
                        help="The signing algorithm")


    args = parser.parse_args()

    pargs = ["openssl", "rsautl"]
    if args.sign:
        pargs.append("-sign")
    else:
        pargs.append("-verify")

    pargs.append("-inkey %s" % args.rsa_file)

    # create the message
    pargs.append("-in %s" % args.msg_file)

    p = subprocess.Popen()