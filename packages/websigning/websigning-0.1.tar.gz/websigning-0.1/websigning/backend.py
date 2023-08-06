from M2Crypto import BIO, Engine, EVP, X509, m2


class Backend(object):
    """Default M2Crypto backend at the moment"""
    def __init__(self):
        self.name = 'M2Crypto backend'

    def load_private_key(self, path):
        try:
            private = EVP.load_key(path)
        except BIO.BIOError, e:
            raise IOError("Failed to load key {path}: {err}"
                          .format(path=path, err=e))

        return private

    def load_certificate(self, path):
        try:
            certificate = X509.load_cert(path)
        except BIO.BIOError, e:
            raise IOError("Failed to load certificate {path}: {err}"
                          .format(path=path, err=e))

        return certificate


class CHILBackend(Backend):

    def __init__(self):
        Engine.load_dynamic()
        self.engine = Engine.Engine('chil')
        if not self.engine.set_default(m2.ENGINE_METHOD_RSA):
            raise IOError("Could not inialize nCipher OpenSSL engine "
                          "properly. Make sure LD_LIBRARY_PATH contains "
                          "/opt/nfast/toolkits/hwcrhk")

    def load_private_key(self, name):
        try:
            private = self.engine.load_private_key(name)
        except Exception, e:  # I have no idea what might get raised
            raise IOError('Failed to load key "{name}" from HSM: {err}'
                          .format(name=name, err=str(e)))

        return private


def get_backend(name):
    if not name:
        return Backend()
    try:
        klass = globals()[name.upper() + 'Backend']
    except KeyError:
        raise ValueError("No support for the {name} HSM".format(name=name))

    return klass()
