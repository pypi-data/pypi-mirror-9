import os
from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(here, 'README.rst')) as f:
    README = f.read()


setup(name='websigning',
      version='0.1',
      description="Application receipt certifier and verifier",
      long_description=README,
      classifiers=[
          "Programming Language :: Python",
      ],
      keywords="web services",
      author='Ryan Tilder',
      author_email="services-dev@mozilla.com",
      url="http://mozilla.org",
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      setup_requires=["nose>=1.3.4",],
      install_requires=["M2Crypto==0.21.1", "PyJWT_mozilla==0.1.4.2",
                        "requests==2.6.0"],
      tests_require=["unittest2==0.5.1"],
      test_suite="websigning",
      entry_points="""\
      [console_scripts]
      check_receipt_keys = websigning.utils:check_keys_main
      """
)
