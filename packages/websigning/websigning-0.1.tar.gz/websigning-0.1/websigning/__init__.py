from websigning.credentials.ephemeral import GeneratedCredentials
from websigning.credentials.jwsplat import JWSplatCredentials
from websigning.credentials.smime import SMIMECredentials

from websigning.sign.receipts import ReceiptSigner
from websigning.sign.xpi import XPISigner


def new_receipt_signer(key_file, cert_file):
    # Don't check the signature on the certificate because outbound HTTP
    # requests from a sensitive server look suspect
    credentials = JWSplatCredentials(key_file, cert_file,
                                     check_cert_signature=False)
    return ReceiptSigner(credentials)


def new_app_signer(key_file, cert_file, ca_cert_file, backend=None):
    credentials = SMIMECredentials(key_file, cert_file, ca_cert_file,
                                   backend=backend)
    return XPISigner(credentials)


def new_addon_signer(key_file, cert_file, dnbase, **kwargs):
    # dnbase should be a dict like object
    credentials = GeneratedCredentials(key_file, cert_file, dnbase, **kwargs)
    return XPISigner(credentials)
