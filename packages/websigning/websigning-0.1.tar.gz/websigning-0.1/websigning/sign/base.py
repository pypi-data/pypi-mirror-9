class Signer(object):

    def __init__(self, credentials):
        self._credentials = credentials

    def credentials(self):
        return self._credentials

    def sign(self, blob):
        raise NotImplementedError()
