# coding=utf-8

MANIFEST = """Manifest-Version: 1.0

Name: test-file
Digest-Algorithms: MD5 SHA1
MD5-Digest: 5BXJnAbD0DzWPCj6Ve/16w==
SHA1-Digest: 5Hwcbg1KaPMqjDAXV/XDq/f30U0=

Name: test-dir/nested-test-file
Digest-Algorithms: MD5 SHA1
MD5-Digest: 53dwfEn/GnFiWp0NQyqWlA==
SHA1-Digest: 4QzlrC8QyhQW1T0/Nay5kRr3gVo=
"""

SIGNATURE = """Signature-Version: 1.0
MD5-Digest-Manifest: dughN2Z8uP3eXIZm7GVpjA==
SHA1-Digest-Manifest: rnDwKcEuRYqy57DFyzwK/Luul+0=
"""

SIGNATURES = SIGNATURE + """
Name: test-file
Digest-Algorithms: MD5 SHA1
MD5-Digest: jf86A0RSFH3oREWLkRAoIg==
SHA1-Digest: 9O+Do4sVlAh82x9ZYu1GbtyNToA=

Name: test-dir/nested-test-file
Digest-Algorithms: MD5 SHA1
MD5-Digest: YHTqD4SINsoZngWvbGIhAA==
SHA1-Digest: lys436ZGYKrHY6n57Iy/EyF5FuI=
"""

CONTINUED_MANIFEST = MANIFEST + """
Name: test-dir/nested-test-dir/nested-test-dir/nested-test-dir/nested-te
 st-file
Digest-Algorithms: MD5 SHA1
MD5-Digest: 53dwfEn/GnFiWp0NQyqWlA==
SHA1-Digest: 4QzlrC8QyhQW1T0/Nay5kRr3gVo=
"""

# Test for 72 byte limit test
BROKEN_MANIFEST = MANIFEST + """
Name: test-dir/nested-test-dir/nested-test-dir/nested-test-dir/nested-test-file
Digest-Algorithms: MD5 SHA1
MD5-Digest: 53dwfEn/GnFiWp0NQyqWlA==
SHA1-Digest: 4QzlrC8QyhQW1T0/Nay5kRr3gVo=
"""

VERY_LONG_MANIFEST = """Manifest-Version: 1.0

Name: test-file
Digest-Algorithms: MD5 SHA1
MD5-Digest: 5BXJnAbD0DzWPCj6Ve/16w==
SHA1-Digest: 5Hwcbg1KaPMqjDAXV/XDq/f30U0=

Name: test-dir/nested-test-file
Digest-Algorithms: MD5 SHA1
MD5-Digest: 53dwfEn/GnFiWp0NQyqWlA==
SHA1-Digest: 4QzlrC8QyhQW1T0/Nay5kRr3gVo=

Name: test-dir/nested-test-dir-0/nested-test-dir-1/nested-test-dir-2/lon
 g-path-name-test
Digest-Algorithms: MD5 SHA1
MD5-Digest: 9bU/UEp83EbO/DWN3Ds/cg==
SHA1-Digest: lIbbwE8/2LFOD00+bJ/Wu80lR/I=
"""

# Test for Unicode
UNICODE_MANIFEST = """Manifest-Version: 1.0

Name: test-dir/súité-höñe.txt
Digest-Algorithms: MD5 SHA1
MD5-Digest: +ZqzWWcMtOrWxs8Xr/tt+A==
SHA1-Digest: B5HkCxgt6fXNr+dWPwXH2aALVWk=
"""
