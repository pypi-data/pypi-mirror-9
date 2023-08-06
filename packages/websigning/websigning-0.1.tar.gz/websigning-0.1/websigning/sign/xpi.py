import hashlib
import itertools
import os.path
import re
import zipfile

from base64 import b64encode, b64decode
from cStringIO import StringIO
from fnmatch import fnmatch

from M2Crypto import Err
from M2Crypto.BIO import BIOError, MemoryBuffer
from M2Crypto.SMIME import SMIME, PKCS7, PKCS7_BINARY, PKCS7_DETACHED
from M2Crypto.X509 import X509_Stack
from M2Crypto.m2 import pkcs7_read_bio_der

from websigning.sign.base import Signer

#
# XPI signing is, technically speaking, a slightly incompatible subset of JAR
# signing.  JAR signing uses PKCS#7 detached signatures in DER format.  The
# incompatibilities are not with the PKCS#7 signatures directly.  There
# is one change from the usual S/MIME signature generation with OpenSSL that
# is needed in order to work correctly with signature verification in the
# expected client(Firefox/Thunderbird/etc. and Fennec codebases).
#
# XPI signature verification goes belly up if there is an SMIME capabilities
# section in the PKCS#7 body.  To prevent this, use flag not currently
# exported by M2Crypto but available in OpenSSL.
#
PKCS7_NOSMIMECAP = 0x200

headers_re = re.compile(
    r"""^((?:Manifest|Signature)-Version
          |Name
          |Digest-Algorithms
          |(?:MD5|SHA1)-Digest(?:-Manifest)?)
          \s*:\s*(.*)""", re.X | re.I)
continuation_re = re.compile(r"""^ (.*)""", re.I)
directory_re = re.compile(r"[\\/]$")


# Files to exclude from a manifest according to the spec:
# noqa http://docs.oracle.com/javase/8/docs/technotes/guides/jar/jar.html#SignedJar-Overview
#
# Matching is case insensitive.
MANIFEST_EXCLUDE = ("META-INF/*.mf",
                    "META-INF/*.sf",
                    "META-INF/*.dsa",
                    "META-INF/*.rsa",
                    "META-INF/sig-*",
                    "META-INF/ids.json")

# Python 2.6 and earlier doesn't have context manager support
ZipFile = zipfile.ZipFile
if not hasattr(zipfile.ZipFile, "__enter__"):
    class ZipFile(zipfile.ZipFile):

        def __enter__(self):
            return self

        def __exit__(self, type, value, traceback):
            self.close()


class ParsingError(Exception):
    pass


def file_key(zinfo):
    '''
    Sort keys for xpi files
    @param name: name of the file to generate the sort key from
    '''
    # Copied from xpisign.py's api.py and tweaked
    name = zinfo.filename
    prio = 4
    if name == 'install.rdf':
        prio = 1
    elif name in ["chrome.manifest", "icon.png", "icon64.png"]:
        prio = 2
    elif name in ["MPL", "GPL", "LGPL", "COPYING", "LICENSE", "license.txt"]:
        prio = 5
    parts = [prio] + list(os.path.split(name.lower()))
    return "%d-%s-%s" % tuple(parts)


def _digest(data):
    md5 = hashlib.md5()
    md5.update(data)
    sha1 = hashlib.sha1()
    sha1.update(data)
    return {'md5': md5.digest(), 'sha1': sha1.digest()}


class Section(object):
    __slots__ = ('name', 'algos', 'digests')

    def __init__(self, name, algos=('md5', 'sha1'), digests={}):
        self.name = name
        self.algos = algos
        self.digests = digests

    def __str__(self):
        # Important thing to note: placement of newlines in these strings is
        # sensitive and should not be changed without reading through
        # http://docs.oracle.com/javase/7/docs/technotes/guides/jar/jar.html#JAR%20Manifest
        # thoroughly.
        algos = ''
        order = self.digests.keys()
        order.sort()
        for algo in order:
            algos += " %s" % algo.upper()
        entry = ''
        # The spec for zip files only supports extended ASCII and UTF-8
        # See http://www.pkware.com/documents/casestudies/APPNOTE.TXT
        # and search for "language encoding" for details
        #
        # See https://bugzilla.mozilla.org/show_bug.cgi?id=1013347
        if isinstance(self.name, unicode):
            name = self.name.encode("utf-8")
        else:
            name = self.name
        name = "Name: %s" % name
        # See https://bugzilla.mozilla.org/show_bug.cgi?id=841569#c35
        while name:
            entry += name[:72]
            name = name[72:]
            if name:
                entry += "\n "
        entry += "\n"
        entry += "Digest-Algorithms:%s\n" % algos
        for algo in order:
            entry += "%s-Digest: %s\n" % (algo.upper(),
                                          b64encode(self.digests[algo]))
        return entry


class Manifest(list):
    version = '1.0'

    def __init__(self, *args, **kwargs):
        super(Manifest, self).__init__(*args)
        for k, v in kwargs.iteritems():
            setattr(self, k, v)

    @classmethod
    def parse(klass, buf):
        # version = None
        if hasattr(buf, 'readlines'):
            fest = buf
        else:
            fest = StringIO(buf)
        # Quick check for truncated or empty files
        position = fest.tell()
        fest.seek(0, 2)
        if fest.tell() - position < 120:
            name = '<memory>'
            if hasattr(fest, 'name'):
                name = fest.name
            raise ParsingError('Attempting to parse a truncated or empty '
                               'file: "{path}"'.format(path=name))
        # Reset to the beginning
        fest.seek(position, 0)

        kwargs = {}
        items = []
        item = {}
        header = ''  # persistent and used for accreting continuations
        lineno = 0
        # JAR spec requires two newlines at the end of a buffer to be parsed
        # and states that they should be appended if necessary.  Just throw
        # two newlines on every time because it won't hurt anything.
        for line in itertools.chain(fest.readlines(), "\n" * 2):
            lineno += 1
            line = line.rstrip()
            if len(line) > 72:
                raise ParsingError("Manifest parsing error: line too long "
                                   "(%d)" % lineno)
            # End of section
            if not line:
                if item:
                    items.append(Section(item.pop('name'), **item))
                    item = {}
                header = ''
                continue
            # continuation?
            continued = continuation_re.match(line)
            if continued:
                if not header:
                    raise ParsingError("Manifest parsing error: continued line"
                                       " without previous header! Line number"
                                       " %d" % lineno)
                item[header] += continued.group(1)
                continue
            match = headers_re.match(line)
            if not match:
                raise ParsingError("Unrecognized line format: \"%s\"" % line)
            header = match.group(1).lower()
            value = match.group(2)
            if '-version' == header[-8:]:
                # Not doing anything with these at the moment
                # payload = header[:-8]
                # version = value.strip()
                pass
            elif '-digest-manifest' == header[-16:]:
                if 'digest_manifests' not in kwargs:
                    kwargs['digest_manifests'] = {}
                kwargs['digest_manifests'][header[:-16]] = b64decode(value)
            elif 'name' == header:
                if directory_re.search(value):
                    continue
                item['name'] = value
                continue
            elif 'digest-algorithms' == header:
                item['algos'] = tuple(re.split('\s*', value.lower()))
                continue
            elif '-digest' == header[-7:]:
                if 'digests' not in item:
                    item['digests'] = {}
                item['digests'][header[:-7]] = b64decode(value)
                continue
        if len(kwargs):
            return klass(items, **kwargs)
        return klass(items)

    @property
    def header(self):
        return "%s-Version: %s" % (type(self).__name__.title(),
                                   self.version)

    @property
    def body(self):
        return "\n".join([str(i) for i in self])

    def __str__(self):
        return "\n".join([self.header, "", self.body])


class Signature(Manifest):
    omit_individual_sections = True
    digest_manifests = {}

    @property
    def digest_manifest(self):
        return ["%s-Digest-Manifest: %s" % (i[0].upper(), b64encode(i[1]))
                for i in sorted(self.digest_manifests.iteritems())]

    @property
    def header(self):
        header = super(Signature, self).header
        return "\n".join([header, ] + self.digest_manifest)

    # So we can omit the individual signature sections
    def __str__(self):
        if self.omit_individual_sections:
            return str(self.header) + "\n"
        return super(Signature, self).__str__()


class JarExtractor(object):
    """
    Walks an archive, creating manifest.mf and signature.sf contents as it goes

    Can also generate a new signed archive, if given a PKCS#7 signature
    """

    def __init__(self, path, outpath=None, ids=None,
                 omit_signature_sections=False):
        """
        """
        self.inpath = path
        self.outpath = outpath
        self._digests = []
        self.omit_sections = omit_signature_sections
        self._manifest = None
        self._sig = None
        self.ids = ids

        def mksection(data, fname):
            digests = _digest(data)
            item = Section(fname, algos=tuple(digests.keys()),
                           digests=digests)
            self._digests.append(item)

        with ZipFile(self.inpath, 'r') as zin:
            for f in sorted(zin.filelist, key=file_key):
                # Skip directories and specific files found in META-INF/ that
                # are not permitted in the manifest
                if directory_re.search(f.filename):
                    continue
                if self.should_exclude(f.filename):
                    continue
                mksection(zin.read(f.filename), f.filename)

            if ids:
                mksection(ids, 'META-INF/ids.json')

    def _sign(self, item):
        digests = _digest(str(item))
        return Section(item.name, algos=tuple(digests.keys()),
                       digests=digests)

    @property
    def manifest(self):
        if not self._manifest:
            self._manifest = Manifest(self._digests)
        return self._manifest

    @property
    def signatures(self):
        # The META-INF/zigbert.sf file contains hashes of the individual
        # sections of the the META-INF/manifest.mf file.  So we generate that
        # here
        if not self._sig:
            self._sig = Signature([self._sign(f) for f in self._digests],
                                  digest_manifests=_digest(str(self.manifest)),
                                  omit_individual_sections=self.omit_sections)
        return self._sig

    @property
    def signature(self):
        # Returns only the x-Digest-Manifest signature and omits the individual
        # section signatures
        return self.signatures.header + "\n"

    def make_signed(self, signature, outpath=None):
        outpath = outpath or self.outpath
        if not outpath:
            raise IOError("No output file specified")

        if os.path.exists(outpath):
            raise IOError("File already exists: %s" % outpath)

        with ZipFile(self.inpath, 'r') as zin:
            with ZipFile(outpath, 'w', zipfile.ZIP_DEFLATED) as zout:
                # zigbert.rsa *MUST* be the first file in the archive to take
                # advantage of Firefox's optimized downloading of XPIs
                zout.writestr("META-INF/zigbert.rsa", signature)
                for f in sorted(zin.infolist()):
                    # Make sure we exclude any of our signature and manifest
                    # files
                    if self.should_exclude(f.filename):
                        continue
                    zout.writestr(f, zin.read(f.filename))
                zout.writestr("META-INF/manifest.mf", str(self.manifest))
                zout.writestr("META-INF/zigbert.sf", str(self.signatures))
                if self.ids is not None:
                    zout.writestr('META-INF/ids.json', self.ids)

    @staticmethod
    def should_exclude(filename):
        for exclude in MANIFEST_EXCLUDE:
            if fnmatch(filename, exclude):
                return True
        return False


# This is basically a dumbed down version of M2Crypto.SMIME.load_pkcs7 but
# that reads DER instead of only PEM formatted files
def get_signature_serial_number(pkcs7):
    """
    Extracts the serial number out of a DER formatted, detached PKCS7
    signature buffer
    """
    pkcs7_buf = MemoryBuffer(pkcs7)
    if pkcs7_buf is None:
        raise BIOError(Err.get_error())

    p7_ptr = pkcs7_read_bio_der(pkcs7_buf.bio)
    p = PKCS7(p7_ptr, 1)

    # Fetch the certificate stack that is the list of signers
    # Since there should only be one in this use case, take the zeroth
    # cert in the stack and return its serial number
    return p.get0_signers(X509_Stack())[0].get_serial_number()


#
# The actual signer
#
class XPISigner(Signer):
    """
    XPISigner handles generating the signature for an XPI.  It is used directly
    for FfxOS privileged app signing and as a base class for addon signing.
    """

    def __init__(self, credentials):
        if (not hasattr(credentials, 'cert_stack')
                or not isinstance(credentials.cert_stack, X509_Stack)):
            raise ValueError("Non-SMIME signing credentials passed to "
                             "XPISigner!")
        self.credentials = credentials

    def sign(self, blob, *args, **kwargs):
        # PKCS#7 object
        smime = SMIME()
        smime.pkey, smime.x509, stack = self.credentials(*args, **kwargs)
        smime.set_x509_stack(stack)

        # Generates the signature as a PKCS#7 blob to a buffer
        pkcs7 = smime.sign(MemoryBuffer(str(blob)),
                           PKCS7_BINARY | PKCS7_DETACHED | PKCS7_NOSMIMECAP)

        # Convert that buffer to DER and return the DER formatted contents
        der_buf = MemoryBuffer()
        pkcs7.write_der(der_buf)
        return der_buf.read()
