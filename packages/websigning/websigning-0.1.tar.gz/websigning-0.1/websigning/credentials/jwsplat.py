import hashlib
import json
import struct
import time

import jwt
import requests

from M2Crypto import BIO, RSA

from websigning.credentials.base import Credentials


# Convert a JWK exponent or modulus from base64 URL safe encoded big endian
# byte string to an OpenSSL MPINT
def jwk2pubkey(jwk):
    __ = jwt.base64url_decode(jwk.encode('ascii'))
    # Cribbed from PyBrowserID's pybrowserid.crypto.m2.int2mpint
    return struct.pack('>I', len(__) + 1) + "\x00" + __


class JWSplatCredentials(Credentials):
    """
    Class for handling Mozilla's weird handling of HSM stored keys that we use
    for JWT signing of signatures.
    """

    def __init__(self, key_path, cert_path,
                 max_cert_lifetime=2 * 24 * 60 * 60,
                 check_cert_signature=False,
                 check_expiration=False):
        self.max_cert_lifetime = max_cert_lifetime
        super(JWSplatCredentials, self).__init__(key_path, cert_path)

        self.check_keys(check_cert_signature, check_expiration)

    def load_private_key(self, path):
        # We expect an RSA key on the local filesystem. *NOT* an HSM stored key
        try:
            self.private = RSA.load_key(path)
        except BIO.BIOError, e:
            raise IOError('Failed to load key {path}: {err}'
                          .format(path=path, err=e))

    def load_certificate(self, path):
        """
        Loads Mozilla's own, very special JWK-in-a-JWT certificate format.

        Attempts to load it as a JWT.  This used to support loading a
        from a JSON file for testing but that made for some wonky code.
        """
        with open(path, 'r') as f:
            self.certificate = f.read()
        try:
            self.cert_data = jwt.decode(self.certificate, verify=False)
        except jwt.DecodeError, e:
            raise IOError('Unable to load JWT certificate: {cert}'
                          .format(cert=e))
        # Convert the JWK into a form usable by M2Crypto
        exp = self.cert_data['jwk'][0]['exp']
        mod = self.cert_data['jwk'][0]['mod']
        try:
            self.public = RSA.new_pub_key((jwk2pubkey(exp),
                                           jwk2pubkey(mod)))
        except Exception, e:
            raise ValueError('Failed to create RSA object from certificate\'s '
                             'JWK: {err}'.format(err=e))

    def check_keys(self, check_cert_signature=False, check_expiration=False):

        if check_expiration:
            now = int(time.time())
            limit = now + self.max_cert_lifetime
            if self.cert_data['exp'] < limit:
                expires = time.asctime(time.gmtime(self.cert_data['exp']))
                raise ValueError('Certificate will expire too soon: {expires} '
                                 'GMT'.format(expires=expires))

        # Check that our private key and public key halves match
        try:
            digest = hashlib.sha256(self.certificate).digest()
            signature = self.private.sign(digest, 'sha256')
            self.public.verify(digest, signature, 'sha256')
        except Exception, e:
            raise ValueError('The keys do not appear to be a matched pair: '
                             '{err}'.format(err=e))

        if check_cert_signature:
            # Fetch the issuer's public key from the URL provided by the key
            try:
                response = requests.get(self.cert_data['iss'])
                if response.status_code == 200:
                    jwk = json.loads(response.text)
                    exp = jwk['jwk'][0]['exp']
                    mod = jwk['jwk'][0]['mod']
                    root = RSA.new_pub_key((jwk2pubkey(exp), jwk2pubkey(mod)))
            except requests.RequestException, e:
                raise ValueError('Failed to fetch {url}: {err}'
                                 .format(url=self.cert_data['iss'],
                                         err=str(e)))
            except Exception, e:
                raise ValueError('Failed to convert root pub key fetched from '
                                 '{url}: {err}'
                                 .format(url=self.cert_data['iss'],
                                         err=str(e)))

            # Verify that our certificate has a valid signature
            try:
                _ = jwt.decode(self.certificate, root, verify=True)  # noqa
            except Exception, e:
                raise ValueError('Failed to verify root key signature on '
                                 'JWT certificate: {err}'.format(err=e))
