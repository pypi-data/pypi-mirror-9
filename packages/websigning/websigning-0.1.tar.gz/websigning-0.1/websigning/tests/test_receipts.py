import jwt
import unittest2

from websigning.credentials.jwsplat import JWSplatCredentials
from websigning.sign.receipts import ReceiptSigner
from websigning.tests.base import PERMITTED_ISSUERS, test_file
from websigning.validators import (
    ReceiptConflict,
    ValidationError,
    valid_receipt)


class ReceiptsTest(unittest2.TestCase):

    @property
    def template(self, **kwargs):
        return dict({"typ": "purchase-receipt",
                     "product": {"url": "https://grumpybadgers.com",
                                 "storedata": "5169314356"},
                     "user": {"type": "email",
                              "value": "pickles@example9.com"},
                     "iss": "https://marketplace-dev.allizom.org",
                     "nbf": self.issuer['iat'],
                     "iat": self.issuer['iat'],
                     "detail": "https://appstore.com/receipt/5169314356",
                     "verify": "https://appstore.com/verify/5169314356"},
                    **kwargs)

    def setUp(self):
        with open(test_file('test_crt.jwk')) as f:
            self.issuer = jwt.decode(f.read(), verify=False)

    def test_01_validate_malformed_json(self):
        receipt = dict(nascar=self.template)
        self.assertRaises(ValidationError, valid_receipt, receipt, None, None)

    def test_02_validate_issuer(self):
        receipt = dict(self.template, iss="Big Bob's Rodeo Dairy!")
        self.assertRaises(ReceiptConflict, valid_receipt, receipt,
                          self.issuer, PERMITTED_ISSUERS)

    def test_03_validate_nbf(self):
        receipt = dict(self.template, nbf=0)
        self.assertRaises(ReceiptConflict, valid_receipt, receipt,
                          self.issuer, PERMITTED_ISSUERS)

        receipt = dict(self.template, nbf=self.issuer['iat'] - 1)
        self.assertRaises(ReceiptConflict, valid_receipt, receipt,
                          self.issuer, PERMITTED_ISSUERS)

        receipt = dict(self.template, nbf=self.issuer['exp'] + 1)
        self.assertRaises(ReceiptConflict, valid_receipt, receipt,
                          self.issuer, PERMITTED_ISSUERS)

    def test_04_validate_iat(self):
        receipt = dict(self.template, iat=0)
        self.assertRaises(ReceiptConflict, valid_receipt, receipt,
                          self.issuer, PERMITTED_ISSUERS)

        receipt = dict(self.template, iat=self.issuer['iat'] - 1)
        self.assertRaises(ReceiptConflict, valid_receipt, receipt,
                          self.issuer, PERMITTED_ISSUERS)

        receipt = dict(self.template, iat=self.issuer['exp'] + 1)
        self.assertRaises(ReceiptConflict, valid_receipt, receipt,
                          self.issuer, PERMITTED_ISSUERS)

    def test_05_cannot_be_issued_in_the_future(self):
        receipt = self.template
        self.assertRaises(ReceiptConflict, valid_receipt, receipt,
                          self.issuer, PERMITTED_ISSUERS, now=0)

    def test_06_timestamp_keys_must_be_numeric(self):
        for receipt_key in ('iat', 'nbf'):
            kw = {receipt_key: 'not-a-number'}
            receipt = dict(self.template, **kw)
            self.assertRaises(ValidationError, valid_receipt, receipt,
                              self.issuer, PERMITTED_ISSUERS)

    def test_07_validate_user(self):
        receipt = dict(self.template, user='not a dict!')
        self.assertRaises(ValidationError, valid_receipt, receipt,
                          self.issuer, PERMITTED_ISSUERS)

        receipt = dict(self.template, user={})
        self.assertRaises(ValidationError, valid_receipt, receipt,
                          self.issuer, PERMITTED_ISSUERS)

        receipt = dict(self.template, user={'type': ''})
        self.assertRaises(ValidationError, valid_receipt, receipt,
                          self.issuer, PERMITTED_ISSUERS)

        receipt = dict(self.template, user={'type': 'taco', 'value': ''})
        self.assertRaises(ValidationError, valid_receipt, receipt,
                          self.issuer, PERMITTED_ISSUERS)

        receipt = dict(self.template, user={'type': 'email', 'value': ''})
        self.assertRaises(ValidationError, valid_receipt, receipt,
                          self.issuer, PERMITTED_ISSUERS)

        receipt = dict(self.template, user={'type': 'email',
                                            'value': 'hal@9000'})
        self.assertRaises(ValidationError, valid_receipt, receipt,
                          self.issuer, PERMITTED_ISSUERS)

    def test_08_validate_product(self):
        receipt = dict(self.template, product='not a dict!')
        self.assertRaises(ValidationError, valid_receipt, receipt,
                          self.issuer, PERMITTED_ISSUERS)

        receipt = dict(self.template, product={})
        self.assertRaises(ValidationError, valid_receipt, receipt,
                          self.issuer, PERMITTED_ISSUERS)

        receipt = dict(self.template, product={'url': ''})
        self.assertRaises(ValidationError, valid_receipt, receipt,
                          self.issuer, PERMITTED_ISSUERS)

        receipt = dict(self.template,
                       product={'url': 'gopher://yoyodyne-propulsion.com'})
        self.assertRaises(ValidationError, valid_receipt, receipt,
                          self.issuer, PERMITTED_ISSUERS)

        receipt = dict(self.template,
                       product={'url': 'https://grumpybadgers.com',
                                'storedata': ''})
        self.assertRaises(ValidationError, valid_receipt, receipt,
                          self.issuer, PERMITTED_ISSUERS)

    def test_09_validate_protocol(self):
        for url in ['http://f.com', 'https://f.com', 'app://f.com']:
            receipt = dict(self.template, product={'url': url,
                                                   'storedata': 's'})
            self.assertTrue(valid_receipt(receipt, self.issuer,
                                          PERMITTED_ISSUERS))

    def test_10_signatures(self):
        # Check credentials first
        credentials = JWSplatCredentials(test_file('test_key.pem'),
                                         test_file('test_crt.jwk'),
                                         check_cert_signature=True)

        payload = {"kermit": "the frog",
                   "miss": "piggy",
                   "rolf": "the dog"}
        signer = ReceiptSigner(credentials)
        # JWT signing is always attached so the payload and the signature
        # are returned as a single JWT encoded blob
        blob = signer.sign(payload)
        self.assertEqual(payload,
                         jwt.decode(blob, credentials.public, verify=True))
