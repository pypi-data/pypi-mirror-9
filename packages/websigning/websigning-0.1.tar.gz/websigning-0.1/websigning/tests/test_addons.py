import unittest2

from M2Crypto import EVP, X509

from websigning.credentials.ephemeral import (
    EphemeralCA,
    EphemeralFactory,
    GeneratedCredentials)
from websigning.sign.xpi import JarExtractor, XPISigner
from websigning.tests.base import (
    compare_x509_names,
    get_signature_cert_subject,
    der_to_pkcs7,
    test_file)
from websigning.tests.data import SIGNATURE, SIGNATURES
from websigning.validators import ValidationError, valid_addon


class AddonsTest(unittest2.TestCase):

    ca_key_file = test_file('addons_test_root_ca_key.pem')
    ca_cert_file = test_file('addons_test_root_ca_cert.pem')
    ephemeral_key_size = 512
    cert_validity_lifetime = 3650
    signature_digest = 'sha256'
    dnbase = {'C': 'US',
              'ST': 'Denial',
              'L': 'Calvinville',
              'O': 'Allizom, Cni.',
              'OU': 'Derivative Knuckles'}
    dnorder = ('C', 'ST', 'L', 'O', 'OU', 'CN')
    extensions = {'basicConstraints': 'CA:false',
                  'subjectKeyIdentifier': 'hash',
                  'authorityKeyIdentifier': 'keyid:always',
                  'keyUsage': 'digitalSignature'}

    def _extract(self, omit=False):
        return JarExtractor(test_file('test-jar.zip'),
                            test_file('test-jar-signed.jar'),
                            omit_signature_sections=omit)

    def gen(self, name='SMRT'):
        e = EphemeralFactory(self.dnbase, key_size=2048)
        return e.new(name)

    def x509_name(self, **attribs):
        name = X509.X509_Name()
        dnbase = dict(self.dnbase, **attribs)
        for k, v in dnbase.items():
            setattr(name, k.upper(), v)
        return name

    def test_00_ephemeral_factory(self):
        # The default identifier value is 'SMRT'
        name = self.x509_name(CN='SMRT')
        key, req = self.gen()
        self.assertTrue(compare_x509_names(req.get_subject(), name))

    def test_01_ephemeral_ca(self):
        test_ca = EphemeralCA(EVP.load_key(self.ca_key_file),
                              X509.load_cert(self.ca_cert_file),
                              self.extensions)
        key1, req1 = self.gen('ephy-1')
        cert1 = test_ca.certify(req1)
        key2, req2 = self.gen('ephy-2')
        cert2 = test_ca.certify(req2)
        self.assertNotEqual(cert1.get_serial_number(),
                            cert2.get_serial_number())

    def test_02_valid_addon(self):
        self.assertTrue(valid_addon('bifur', SIGNATURE))
        self.assertTrue(valid_addon('bofur', SIGNATURES))
        self.assertRaises(ValidationError, valid_addon, 'bombur',
                          SIGNATURES + '\nlozenges are tasty')
        self.assertRaises(ValidationError, valid_addon, 'ori',
                          SIGNATURE)
        # Need a string at least 128 bytes long to break validatoin
        dwarves = ('thorin', 'fili', 'kili', 'balin', 'dwalin', 'oin', 'gloin',
                   'ori', 'dori', 'nori', 'bifur', 'bofur', 'bombur')
        dwarvish = ' '.join(dwarves)
        dwarvish = dwarvish * 2
        self.assertRaises(ValidationError, valid_addon, dwarvish,
                          SIGNATURE)

    def test_03_sign_addons(self):
        name = self.x509_name(OU='Pickle Processing',
                              CN='hot_pink_bougainvillea')
        credentials = GeneratedCredentials(self.ca_key_file,
                                           self.ca_cert_file,
                                           dict(self.dnbase,
                                                OU='Pickle Processing'))
        signer = XPISigner(credentials)
        extracted = self._extract(True)
        signature = signer.sign(extracted, 'hot_pink_bougainvillea')

        # The signer returns DER formatted PKCS7 blobs so it is necessary to
        # convert back to PKCS7 object

        # See the note in test_xpi.py's test_01_signer_test method for why
        # this isn't a one liner.
        pkcs7 = der_to_pkcs7(signature)
        signature_subject = get_signature_cert_subject(pkcs7)
        self.assertTrue(compare_x509_names(signature_subject, name))
