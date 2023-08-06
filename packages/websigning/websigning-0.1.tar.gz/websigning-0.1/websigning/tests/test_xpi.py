import os.path
import hashlib
import shutil
import tempfile
import unittest2

from websigning.credentials.smime import SMIMECredentials
from websigning.sign.xpi import (
    Manifest,
    JarExtractor,
    ParsingError,
    XPISigner,
    ZipFile,
    file_key,
    get_signature_serial_number
)
from websigning.tests.base import (
    der_to_pkcs7,
    get_signature_cert_subject,
    test_file)
from websigning.tests.data import (
    MANIFEST,
    SIGNATURE,
    SIGNATURES,
    CONTINUED_MANIFEST,
    BROKEN_MANIFEST,
    VERY_LONG_MANIFEST,
    UNICODE_MANIFEST)


class JARExtractorTest(unittest2.TestCase):

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp(prefix='tmp-signing-clients-test-')
        self.addCleanup(lambda: shutil.rmtree(self.tmpdir))

    def tmp_file(self, fname):
        return os.path.join(self.tmpdir, fname)

    def _extract(self, omit=False):
        return JarExtractor(test_file('test-jar.zip'),
                            omit_signature_sections=omit)

    def test_00_extractor(self):
        self.assertTrue(isinstance(self._extract(), JarExtractor))

    def test_01_manifest(self):
        extracted = self._extract()
        self.assertEqual(str(extracted.manifest), MANIFEST)

    def test_02_signature(self):
        extracted = self._extract()
        self.assertEqual(str(extracted.signature), SIGNATURE)

    def test_03_signatures(self):
        extracted = self._extract()
        self.assertEqual(str(extracted.signatures), SIGNATURES)

    def test_04_signatures_omit(self):
        extracted = self._extract(True)
        self.assertEqual(str(extracted.signatures), SIGNATURE)

    def test_05_continuation(self):
        manifest = Manifest.parse(CONTINUED_MANIFEST)
        self.assertEqual(str(manifest), CONTINUED_MANIFEST)

    def test_06_line_too_long(self):
        self.assertRaises(ParsingError, Manifest.parse, BROKEN_MANIFEST)

    def test_07_wrapping(self):
        extracted = JarExtractor(test_file('test-jar-long-path.zip'),
                                 omit_signature_sections=False)
        self.assertEqual(str(extracted.manifest), VERY_LONG_MANIFEST)

    def test_08_unicode(self):
        extracted = JarExtractor(test_file('test-jar-unicode.zip'),
                                 omit_signature_sections=False)
        self.assertEqual(str(extracted.manifest), UNICODE_MANIFEST)

    def test_09_serial_number_extraction(self):
        with open(test_file('zigbert.test.pkcs7.der'), 'r') as f:
            serialno = get_signature_serial_number(f.read())
        # Signature occured on Thursday, January 22nd 2015 at 11:02:22am PST
        # The signing service returns a Python time.time() value multiplied
        # by 1000 to get a (hopefully) truly unique serial number
        self.assertEqual(1421953342960, serialno)

    def test_10_resigning_manifest_exclusions(self):
        # This zip contains META-INF/manifest.mf, META-INF/zigbert.sf, and
        # META-INF/zigbert.rsa in addition to the contents of the basic test
        # archive test-jar.zip
        extracted = JarExtractor(test_file('test-jar-meta-inf-exclude.zip'),
                                 omit_signature_sections=True)
        self.assertEqual(str(extracted.manifest), MANIFEST)

    def test_11_make_signed(self):
        extracted = JarExtractor(test_file('test-jar.zip'),
                                 omit_signature_sections=True)

        # Generate the signature
        credentials = SMIMECredentials(test_file('xpi_test_key.pem'),
                                       test_file('xpi_test_cert.pem'),
                                       test_file('xpi_test_cert.pem'))
        signer = XPISigner(credentials)
        signature = signer.sign(str(extracted.signatures))
        signature_digest = hashlib.sha1(signature)

        signed_file = self.tmp_file('test-jar-signed.zip')
        extracted.make_signed(signature, signed_file)

        # Make sure the manifest is correct
        signed = JarExtractor(signed_file, omit_signature_sections=True)
        self.assertEqual(str(extracted.manifest), str(signed.manifest))

        # Verify the signed zipfile's contents
        with ZipFile(signed_file, 'r') as zin:
            # sorted(...) should result in the following order:
            files = ['test-file', 'META-INF/manifest.mf',
                     'META-INF/zigbert.rsa', 'META-INF/zigbert.sf',
                     'test-dir/', 'test-dir/nested-test-file']
            signed_files = [f.filename for f in sorted(zin.filelist,
                                                       key=file_key)]
            self.assertEqual(files, signed_files)
            zip_sig_digest = hashlib.sha1(zin.read('META-INF/zigbert.rsa'))
            self.assertEqual(signature_digest.hexdigest(),
                             zip_sig_digest.hexdigest())


class XPITest(unittest2.TestCase):

    def test_01_signer_test(self):
        credentials = SMIMECredentials(test_file('xpi_test_key.pem'),
                                       test_file('xpi_test_cert.pem'),
                                       test_file('xpi_test_cert.pem'))
        signer = XPISigner(credentials)
        signature = signer.sign(MANIFEST)

        # The signer returns DER formatted PKCS7 blobs so it is necessary to
        # convert back to PKCS7 object

        # Here's a doozie:
        # The following one liner causes segfaults 90%+ of the time on my
        # laptop. The two following lines are the same function calls as the
        # one liner but I presume that the Python GC collects in between and
        # that is just enough of a delay to prevent whatever god awful race
        # condition is getting tickled.
        #
        # noqa signature_subject = get_signature_cert_subject(der_to_pkcs7(signature))
        #
        pkcs7 = der_to_pkcs7(signature)
        signature_subject = get_signature_cert_subject(pkcs7)
        self.assertEqual(str(signature_subject),
                         '/C=UN/ST=Denial/L=Calvinville'
                         '/O=Sprinting Llamas, Inc.'
                         '/CN=Llama Operations Group')
