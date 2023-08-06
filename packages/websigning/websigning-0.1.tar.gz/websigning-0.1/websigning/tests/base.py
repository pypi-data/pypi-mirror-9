import os

# Needed to inspect signatures
from M2Crypto import Err
from M2Crypto.BIO import BIOError, MemoryBuffer
from M2Crypto.SMIME import PKCS7
from M2Crypto.X509 import X509_Stack
from M2Crypto.m2 import pkcs7_read_bio_der


PERMITTED_ISSUERS = ('https://donkeykong.com',
                     'https://pentavirate.com',
                     'https://marketplace-dev.allizom.org',
                     'https://marketplace-dev-cdn.allizom.org/public_keys/' +
                     'test_root_pub.jwk')


def test_file(fname):
    return os.path.join(os.path.dirname(__file__), 'files', fname)


test_file.__test__ = False


def der_to_pkcs7(der):
    pkcs7_buf = MemoryBuffer(der)
    if pkcs7_buf is None:
        raise BIOError(Err.get_error())

    p7_ptr = pkcs7_read_bio_der(pkcs7_buf.bio)
    pkcs7 = PKCS7(p7_ptr, 1)
    return pkcs7


def get_signature_serial_number(pkcs7):
    # Fetch the certificate stack that is the list of signers.
    # Since there should only be one in this use case, take the zeroth
    # cert in the stack and return its serial number
    return pkcs7.get0_signers(X509_Stack())[0].get_serial_number()


def get_signature_cert_subject(pkcs7):
    # Fetch the certificate stack that is the list of signers.
    # Since there should only be one in this use case, take the zeroth
    # cert in the stack and return its serial number
    return pkcs7.get0_signers(X509_Stack())[0].get_subject()


def compare_x509_names(a, b):
    # This is necessary because M2Crypto and OpenSSL are inconsistently
    # segfaulting when I try to be more explicit about it.  If M2Crypto
    # actually exported OpenSSL's X509_NAME_cmp this wouldn't be an issue.
    astring = str(a)
    bstring = str(b)
    if len(astring) != len(bstring):
        return False

    # Convert the strings to dicts since they can be inconsistent order.
    # The strings look like:
    # noqa /C=US/CN=SMRT/OU=Derivative Knuckles/L=Calvinville/O=Allizom, Cni./ST=Denial
    adict = {}
    bdict = {}
    for s, d in ((astring, adict), (bstring, bdict)):
        for i in s.split('/')[1:]:
            b = i.split('=')
            d[b[0]] = b[1]
    return adict == bdict
