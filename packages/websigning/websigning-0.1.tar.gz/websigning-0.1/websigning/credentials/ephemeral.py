import time

from M2Crypto import ASN1, BIO, EVP, RSA, X509

from websigning.credentials.smime import SMIMECredentials


class GeneratedCredentials(SMIMECredentials):

    def __init__(self, ca_priv_key, ca_cert, subject_dn_base,
                 key_size=2048, validity_lifetime=365, digest_alg='sha256',
                 cert_extensions={}, backend=None):
        """
        Generates an ephemeral key that is one-time-use only.  The generated
        key may remain in memory for a period of time but is otherwise not
        stored.

        Parameters:

        ca_priv_key:

        ca_cert:

        key_size: size of the key to create in bits

        validity_lifetime: number of days the signature is valid. Default: 365

        signature_digest_alg: which digest algorithm to use when signing.
                 Default is SHA256

        cert_extensions: a dict of which extensions to apply to the
                 certficate of the generated key

        dn_base: a dict representing the base for the generated certificate's
                 subject's distinguished name(DN).  It should probably contain
                 at least the C, ST, L, and O attributes.  When signing
                 occurs, an identifier for the generated key is expected to be
                 passed in to uniquely identify the key.  This value will
                 populate the CN attribute.
        """
        self.private_path = ca_priv_key
        self.public_path = ca_cert
        super(GeneratedCredentials, self).__init__(ca_priv_key, ca_cert,
                                                   ca_cert,
                                                   backend=backend)

        # The ephemeral key and cert request factory
        self.factory = EphemeralFactory(subject_dn_base, key_size, digest_alg)

        # The authority that signs the ephemeral certificate requests into
        # certificates
        self.ca = EphemeralCA(ca_priv_key, ca_cert, cert_extensions,
                              lifetime=validity_lifetime,
                              digest_alg=digest_alg)

    def __call__(self, identifier):
        # New ephemeral for each request
        ephemeral_key, ephemeral_req = self.factory.new(identifier)
        ephemeral_cert = self.ca.certify(ephemeral_req)
        return ephemeral_key, ephemeral_cert, self.cert_stack


class EphemeralCA(object):
    """
    A convenience object that tries to encompass the majority of the functions
    associated with a certificate authority.
    """
    def __init__(self, ca_priv_key, ca_certificate, extensions, lifetime=365,
                 digest_alg='sha256'):
        if type(ca_priv_key) == str:
            self.key_path = ca_priv_key
            try:
                self.key = EVP.load_key(ca_priv_key)
            except BIO.BIOError, e:
                raise IOError('Failed to load CA private key "{key}" for '
                              'ephemeral key generation: {err}'
                              .format(key=ca_priv_key, err=e))
        else:
            self.key = ca_priv_key
            self.key_path = '<memory>'

        if type(ca_certificate) == str:
            self.certificate_path = ca_certificate
            try:
                self.certificate = X509.load_cert(ca_certificate)
            except BIO.BIOError, e:
                raise IOError('Failed to load certificate {cert}: {err}'
                              .format(cert=ca_certificate, err=e))
        else:
            self.certificate = ca_certificate
            self.certificate_path = '<memory>'

        self.lifetime = lifetime
        self.digest_alg = digest_alg
        # Safe-ish default extensions
        if not extensions:
            extensions = {'basicConstraints': 'CA:false',
                          'subjectKeyIdentifier': 'hash',
                          'authorityKeyIdentifier': 'keyid:always',
                          'keyUsage': 'digitalSignature'}
        self.extensions = extensions

    def set_validity_period(self, cert):
        now = long(time.time())
        asn1 = ASN1.ASN1_UTCTIME()
        asn1.set_time(now)
        cert.set_not_before(asn1)
        asn1 = ASN1.ASN1_UTCTIME()
        asn1.set_time(now + self.lifetime * 24 * 60 * 60)
        cert.set_not_after(asn1)

    def certify(self, req):
        pubkey = req.get_pubkey()
        cert = X509.X509()
        cert.set_pubkey(pubkey)
        cert.set_version(2)  # 2 means X509v3
        #
        # We are explicitly using Python's default time type * 1000 to include
        # milliseconds.  While I don't expect to be generating these more often
        # than once a second I've be wrong before.
        #
        cert.set_serial_number(int(time.time() * 1000))
        self.set_validity_period(cert)

        cert.set_subject(req.get_subject())
        cert.set_pubkey(req.get_pubkey())

        cert.set_issuer(self.certificate.get_subject())

        # Some massaging is necessary for extensions if provided in OpenSSL
        # config file style
        if ('subjectKeyIdentifier' in self.extensions
                and self.extensions['subjectKeyIdentifier'] == 'hash'):
            self.extensions['subjectKeyIdentifier'] = cert.get_fingerprint()

        # Aaaaaand sign
        cert.sign(self.key, self.digest_alg)
        return cert


class EphemeralFactory(object):
    """
    Simply generating ephemeral keys and certificate requests based on settings
    passed in from the config
    """

    def __init__(self, dnbase, key_size=2048, digest_alg='sha256'):
        self.dnbase = dnbase
        self.key_size = key_size
        self.digest_alg = digest_alg

    def new(self, identifier):
        # New key of the correct size
        key = EVP.PKey()
        key.assign_rsa(RSA.gen_key(self.key_size, 0x10001, lambda: None))

        # Generate the certreq
        request = X509.Request()
        request.set_pubkey(key)

        # Set the request's DN
        subject = request.get_subject()
        for k, v in self.dnbase.iteritems():
            # INI style parsers frequently convert key names to all lowercase
            # and M2Crypto's X509_Name class doesn't like that.
            setattr(subject, k.upper(), v)
        subject.CN = identifier

        # Sign the request
        request.sign(key, self.digest_alg)
        return key, request
