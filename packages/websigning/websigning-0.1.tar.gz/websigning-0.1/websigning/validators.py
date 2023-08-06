import re
import time

from datetime import datetime as dt

from websigning.sign.xpi import ParsingError, Signature


# From https://github.com/mozilla/browserid/blob/dev/lib/sanitize.js
EMAIL_REGEX = re.compile(
    "^[-\w.!#$%&'*+/=?\^`{|}~]+@[-a-z\d_]+(\.[-a-z\d_]+)+$", re.I)
PROD_URL_REGEX = re.compile(
    "^(https?|app):\/\/[-a-z\d_]+(\.[-a-z\d_]+)*(:\d+)?$", re.I)

# TODO
#    Don't permit other than the required fields to be safe:
#      typ, nbf, iss, iat, detail, verify, product(url, storedata),
#      user(type, value)


class _Error(Exception):

    def __init__(self, short_message, log_message=None):
        self.short_msg = short_message
        if log_message is None:
            self.log_msg = short_message
        else:
            self.log_msg = log_message

    def __str__(self):
        return self.short_msg


class ValidationError(_Error):
    """
    Raised when an addon, FfxOS app, or receipt fails to validate
    """


class ReceiptConflict(_Error):
    """
    For when a receipt has invalid timestamps of one sort or another
    """


def valid_receipt(receipt, signing, permitted_issuers, now=None):
    """
    Validates the contents of a webapp receipt to a minimal degree
    """

    if now is None:
        now = long(time.time())

    for key in ('detail', 'verify', 'user', 'product', 'iss', 'iat', 'nbf'):
        if key not in receipt:
            raise ValidationError('Required key "{key}" missing'
                                  .format(key=key))

    # Verify the time windows
    #
    # Note: these checks should really reflect a window of opportunity taking
    #       clock drift and processing queue length/times into account
    #
    # Also, if we aren't going to revoke then the checks against signing['exp']
    # should definitely include a window
    if receipt['iss'] not in permitted_issuers:
        raise ReceiptConflict('Unrecognized issuer: "{iss}"'
                              .format(iss=receipt['iss']))

    for receipt_key in ('iat', 'nbf'):
        if not isinstance(receipt[receipt_key], (int, long, float)):
            raise ValidationError('non-numeric timestamp for {key}'
                                  .format(key=receipt_key),
                                  'invalid receipt: non-numeric timestamp for '
                                  '{key}: "{val}"; receipt: {receipt}'
                                  .format(key=receipt_key,
                                          val=receipt[receipt_key],
                                          receipt=receipt))

    if receipt['nbf'] < signing['iat']:
        raise ReceiptConflict("nbf(not before) of receipt < iat(issued at) of "
                              "signing cert",
                              'invalid receipt: nbf {nbf} < iat {iat} of '
                              'signing cert; receipt: {receipt}'
                              .format(nbf=dt.utcfromtimestamp(receipt['nbf']),
                                      iat=dt.utcfromtimestamp(signing['iat']),
                                      receipt=receipt))

    if receipt['nbf'] > signing['exp']:
        raise ReceiptConflict('nbf(not before) of receipt > exp(expires at) '
                              'of signing cert',
                              'invalid receipt: nbf {nbf} > exp {exp} of '
                              'signing cert; receipt: {receipt}'
                              .format(nbf=dt.utcfromtimestamp(receipt['nbf']),
                                      exp=dt.utcfromtimestamp(signing['exp']),
                                      receipt=receipt))

    if receipt['iat'] < signing['iat']:
        raise ReceiptConflict('iat(issued at) of receipt < iat(issued at) of '
                              'signing cert',
                              'invalid receipt: receipt iat {r} < iat {c} of '
                              'signing cert; receipt: {receipt}'
                              .format(r=dt.utcfromtimestamp(receipt['iat']),
                                      c=dt.utcfromtimestamp(signing['iat']),
                                      receipt=receipt))

    if receipt['iat'] > signing['exp']:
        raise ReceiptConflict('iat(issued at) of receipt > exp(expires at) of '
                              'signing cert',
                              'invalid receipt: iat {iat} > exp {exp} of '
                              'signing cert; receipt: {receipt}'
                              .format(iat=dt.utcfromtimestamp(receipt['iat']),
                                      exp=dt.utcfromtimestamp(signing['exp']),
                                      receipt=receipt))

    if receipt['iat'] > now:
        raise ReceiptConflict('iat(issued at) of receipt is in the future',
                              'invalid receipt: iat {iat} > now {now}; '
                              'receipt: {receipt}'
                              .format(iat=dt.utcfromtimestamp(receipt['iat']),
                                      now=dt.utcfromtimestamp(now),
                                      receipt=receipt))

    try:
        valid_user(receipt['user'])
        valid_product(receipt['product'])
    except ValidationError, exc:
        exc.log_msg = 'invalid receipt: {short}: receipt: ' \
                      '{receipt}'.format(short=exc.short_msg,
                                         receipt=receipt)
        raise exc
    return True


def valid_user(obj):
    if type(obj) != dict:
        raise ValidationError('invalid user struct: not a dict')
    if 'type' not in obj:
        raise ValidationError('invalid user struct: no type defined')
    if 'value' not in obj:
        raise ValidationError('invalid user struct: invalid value')
    if obj['type'] not in ('email', 'directed-identifier'):
        raise ValidationError('invalid user struct: unknown type')
    if obj['type'] == 'email' and not EMAIL_REGEX.match(obj['value']):
        raise ValidationError('invalid user struct: invalid value')
    return True


def valid_product(obj):
    if type(obj) != dict:
        raise ValidationError('invalid product struct: not a dict')
    if 'url' not in obj:
        raise ValidationError('invalid product struct: no URL provided')
    if 'storedata' not in obj:
        raise ValidationError('invalid product struct: no storedata')
    if not PROD_URL_REGEX.match(obj['url']):
        raise ValidationError('invalid product struct: URL doesn\'t look '
                              'like http://, https:// or app://: "{0}"'
                              .format(obj['url']))
    if len(obj['storedata']) < 1:
        raise ValidationError('invalid product struct: storedata appears to '
                              'be empty')
    return True


def valid_app(jar_signature):
    """
    Not much validating to do, really.  So much validation is done by the
    separate validation service that we rely pretty heavily on the client
    end of this request doing its job.

    We can use the signature parser to at least make sure the signature is
    nominally correctly formatted.
    """

    try:
        Signature.parse(jar_signature)
    except ParsingError, e:
        raise ValidationError('Provided XPI signature file does not parse: '
                              '"{0}"'.format(e))

    return True


def valid_addon(identifier, jar_signature):
    """
    At the moment a reasonable bounds check on length of the addon id is about
    all I'm certain is acceptable.
    """
    if len(identifier) < 4:
        raise ValidationError('addon_id is very short(<4 bytes): "{0}"'
                              .format(identifier))

    if len(identifier) > 128:
        raise ValidationError('addon_id is very long(>128 bytes): "{0}"'
                              .format(identifier))

    return valid_app(jar_signature)
