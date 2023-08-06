import jwt

from websigning.sign.base import Signer


class ReceiptSigner(Signer):

    def __init__(self, credentials):
        super(ReceiptSigner, self).__init__(credentials)
        self.cert_data = self._credentials.cert_data
        self.certificate = self._credentials.certificate

    def sign(self, blob, algorithm='RS256'):
        private = self._credentials.private
        cert_data = self._credentials.cert_data
        key_type = cert_data['jwk'][0]['alg']

        if key_type[0] != algorithm[0]:
            raise ValueError('Chosen signing algorithm "{algo}" is not '
                             'compatible with a signing key of type {type}'
                             .format(algo=algorithm, type=key_type))

        header = dict(alg=u'RS256', typ='JWT', jku=cert_data['iss'])
        return jwt.encode(blob, private, header=header, algorithm='RS256')
