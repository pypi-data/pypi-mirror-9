from M2Crypto import X509

from websigning.credentials.base import Credentials


class SMIMECredentials(Credentials):
    """
    Base class for SMIME credentials.  Includes a certificate
    chain for inclusion in the PKCS7 signature.
    """

    def __init__(self, private, public, ca_cert_chain, backend=None):
        super(SMIMECredentials, self).__init__(private, public,
                                               backend=backend)

        self.ca_cert_chain_path = ca_cert_chain
        self.load_certificate_chain()

        self.check_certs()

    def load_certificate_chain(self):
        begin_tag = '-----BEGIN CERTIFICATE-----'
        end_tag = '-----END CERTIFICATE-----'

        with open(self.ca_cert_chain_path, 'r') as f:
            chain = f.read()

        current = 0
        stack = X509.X509_Stack()
        while True:
            start = chain.find(begin_tag, current)
            current = chain.find(end_tag) + len(end_tag)
            # End of the file
            if current == len(chain) - 1:
                break
            # Incomplete file but only if we aren't at already at the end
            if start < 0:
                raise ValueError("Truncated or corrupted certificate "
                                 "chain: {chain}"
                                 .format(chain=self.ca_cert_chain_path))
            pem_string = chain[start:current]
            cert = X509.load_cert_string(pem_string)
            if (cert.get_subject().as_text() ==
                    self.public.get_subject().as_text()):
                continue
            stack.push(cert)
        self.cert_stack = stack

    def check_certs(self):
        pass

    def __call__(self, *args, **kwargs):
        return self.private, self.public, self.cert_stack
