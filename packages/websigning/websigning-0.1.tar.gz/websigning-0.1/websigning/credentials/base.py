from M2Crypto import BIO, EVP, X509

from websigning.backend import get_backend


class Credentials(object):
    """
    Base class for cryptographic credentials.  Handles any kind of key that
    OpenSSL's EVP functions do.
    """

    def __init__(self, private, public, backend=None):
        self.backend = get_backend(backend)

        self.private_path = private
        self.load_private_key(private)

        self.public_path = public
        self.load_certificate(public)

        # Check that they're a matching pair
        self.check_keys()

    def load_private_key(self, path):
        if self.backend:
            self.private = self.backend.load_private_key(path)
            return

        try:
            self.private = EVP.load_key(path)
        except BIO.BIOError, e:
            raise IOError("Failed to load private key {path}: {err}"
                          .format(path=path, err=e))

    def load_certificate(self, path):
        try:
            self.public = X509.load_cert(path)
        except BIO.BIOError, e:
            raise IOError("Failed to load certificate {path}: {err}"
                          .format(path=path, err=e))

    def check_keys(self):
        test_string = "This is a test string for testing."
        self.private.sign_init()
        self.private.sign_update(test_string)
        signature = self.private.sign_final()

        public = self.public.get_pubkey()
        public.verify_init()
        public.verify_update(test_string)
        if public.verify_final(signature) != 1:
            raise ValueError("Mismatched private and cert/public keys! {0} "
                             "and {1} do not seem to match."
                             .format(self.private_path, self.public_path))

    def __call__(self, *args, **kwargs):
        return self.private, self.public
