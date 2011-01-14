"""tests for passlib.hash.pbkdf2"""
#=========================================================
#imports
#=========================================================
from __future__ import with_statement
#core
from binascii import unhexlify
import hashlib
import warnings
from logging import getLogger
#site
#pkg
from passlib.tests.utils import TestCase, enable_suite
from passlib.util import H64
import passlib.hash.pbkdf2 as mod
from passlib.tests.test_hash_base import _CryptTestCase as CryptTestCase
#module
log = getLogger(__name__)

###=========================================================
###test frontend class
###=========================================================
##class UnixCryptTest(CryptTestCase):
##    "test UnixCrypt algorithm"
##    alg = mod.UnixCrypt
##    positive_knowns = (
##        #secret, example hash which matches secret
##        ('', 'OgAwTx2l6NADI'),
##        (' ', '/Hk.VPuwQTXbc'),
##        ('test', 'N1tQbOFcM5fpg'),
##        ('Compl3X AlphaNu3meric', 'um.Wguz3eVCx2'),
##        ('4lpHa N|_|M3r1K W/ Cur5Es: #$%(*)(*%#', 'sNYqfOyauIyic'),
##        ('AlOtBsOl', 'cEpWz5IUCShqM'),
##        (u'hell\u00D6', 'saykDgk3BPZ9E'),
##        )
##    invalid_identify = (
##        #bad char in otherwise correctly formatted hash
##        '!gAwTx2l6NADI',
##        )
##    negative_identify = (
##        #hashes using other algs, which shouldn't match this algorithm
##        '$6$rounds=123456$asaltof16chars..$BtCwjqMJGx5hrJhZywWvt0RLE8uZ4oPwc',
##        '$1$dOHYPKoP$tnxS1T8Q6VVn3kpV8cN6o.'
##        )

#=========================================================
#test activate backend (stored in mod._crypt)
#=========================================================
class Pbkdf2BackendTest(TestCase):
    "test builtin unix crypt backend"
    case_prefix = "builtin pbkdf2() backend"

    disable_m2crypto = True

    def setUp(self):
        #disable m2crypto support so we'll run fully in software mode
        if self.disable_m2crypto:
            self._orig_EVP = mod._EVP
            mod._EVP = None

    def cleanUp(self):
        if self.disable_m2crypto:
            mod._EVP = self._orig_EVP

    def test_rfc3962(self):
        "rfc3962 test vectors"
        self.assertFunctionResults(mod.pbkdf2, [
            # result, secret, salt, rounds, keylen, digest="sha1"

            #test case 1 / 128 bit
            (
                unhexlify("cdedb5281bb2f801565a1122b2563515"),
                "password", "ATHENA.MIT.EDUraeburn", 1, 16
            ),

            #test case 2 / 128 bit
            (
                unhexlify("01dbee7f4a9e243e988b62c73cda935d"),
                "password", "ATHENA.MIT.EDUraeburn", 2, 16
            ),

            #test case 2 / 256 bit
            (
                unhexlify("01dbee7f4a9e243e988b62c73cda935da05378b93244ec8f48a99e61ad799d86"),
                "password", "ATHENA.MIT.EDUraeburn", 2, 32
            ),

            #test case 3 / 256 bit
            (
                unhexlify("5c08eb61fdf71e4e4ec3cf6ba1f5512ba7e52ddbc5e5142f708a31e2e62b1e13"),
                "password", "ATHENA.MIT.EDUraeburn", 1200, 32
            ),

            #test case 4 / 256 bit
            (
                unhexlify("d1daa78615f287e6a1c8b120d7062a493f98d203e6be49a6adf4fa574b6e64ee"),
                "password", '\x12\x34\x56\x78\x78\x56\x34\x12', 5, 32
            ),

            #test case 5 / 256 bit
            (
                unhexlify("139c30c0966bc32ba55fdbf212530ac9c5ec59f1a452f5cc9ad940fea0598ed1"),
                "X"*64, "pass phrase equals block size", 1200, 32
            ),

            #test case 6 / 256 bit
            (
                unhexlify("9ccad6d468770cd51b10e6a68721be611a8b4d282601db3b36be9246915ec82a"),
                "X"*65, "pass phrase exceeds block size", 1200, 32
            ),
        ])

    def test_invalid_rounds(self):
        self.assertRaises(ValueError, mod.pbkdf2, 'password', 'salt', -1, 16)
        self.assertRaises(ValueError, mod.pbkdf2, 'password', 'salt', 0, 16)

    def test_invalid_keylen(self):
        self.assertRaises(ValueError, mod.pbkdf2, 'password', 'salt', 1, 20*(2**32))

    def test_sha512_string(self):
        "test alternate digest string (sha512)"
        self.assertFunctionResults(mod.pbkdf2, [
            # result, secret, salt, rounds, keylen, digest="sha1"

            #case taken from example in http://grub.enbug.org/Authentication
            (
               unhexlify("887CFF169EA8335235D8004242AA7D6187A41E3187DF0CE14E256D85ED97A97357AAA8FF0A3871AB9EEFF458392F462F495487387F685B7472FC6C29E293F0A0"),
               "hello",
               unhexlify("9290F727ED06C38BA4549EF7DE25CF5642659211B7FC076F2D28FEFD71784BB8D8F6FB244A8CC5C06240631B97008565A120764C0EE9C2CB0073994D79080136"),
               10000, 64, "sha512"
            ),
        ])

    def test_sha512_function(self):
        "test alternate digest function (sha512)"
        self.assertFunctionResults(mod.pbkdf2, [
            # result, secret, salt, rounds, keylen, digest="sha1"

            #case taken from example in http://grub.enbug.org/Authentication
            (
               unhexlify("887CFF169EA8335235D8004242AA7D6187A41E3187DF0CE14E256D85ED97A97357AAA8FF0A3871AB9EEFF458392F462F495487387F685B7472FC6C29E293F0A0"),
               "hello",
               unhexlify("9290F727ED06C38BA4549EF7DE25CF5642659211B7FC076F2D28FEFD71784BB8D8F6FB244A8CC5C06240631B97008565A120764C0EE9C2CB0073994D79080136"),
               10000, 64, hashlib.sha512
            ),
        ])

if mod._EVP:
    class M2Crypto_Pbkdf2BackendTest(Pbkdf2BackendTest):
        disable_m2crypto = False
        case_prefix = "m2crypto pbkdf2() backend"

#=========================================================
#EOF
#=========================================================