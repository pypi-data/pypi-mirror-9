__version__ = '2.1'

import io
import os
import sys

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
with io.open(os.path.join(here, 'README.rst'), encoding='utf8') as f:
    README = f.read()
with io.open(os.path.join(here, 'CHANGELOG.rst'), encoding='utf8') as f:
    CHANGES = f.read()
PY3 = sys.version_info[0] == 3

extra_options = {
    "packages": find_packages(),
    }

if PY3:
    extra_options["use_2to3"] = True
    if "test" in sys.argv or "develop" in sys.argv:
        for root, directories, files in os.walk("tests"):
            for directory in directories:
                extra_options["packages"].append(os.path.join(root, directory))

setup(name="Routes",
      version=__version__,
      description='Routing Recognition and Generation Tools',
      long_description=README + '\n\n' + CHANGES,
      classifiers=["Development Status :: 5 - Production/Stable",
                   "Intended Audience :: Developers",
                   "License :: OSI Approved :: MIT License",
                   "Topic :: Internet :: WWW/HTTP",
                   "Topic :: Software Development :: Libraries :: Python Modules",
                   "Programming Language :: Python :: Implementation :: PyPy",
                   "Programming Language :: Python :: Implementation :: CPython",
                   'Programming Language :: Python',
                   "Programming Language :: Python :: 2",
                   "Programming Language :: Python :: 2.6",
                   "Programming Language :: Python :: 2.7",
                   "Programming Language :: Python :: 3",
                   "Programming Language :: Python :: 3.2",
                   "Programming Language :: Python :: 3.3",
                   "Programming Language :: Python :: 3.4"
                   ],
      keywords='routes webob dispatch',
      author="Ben Bangert",
      author_email="ben@groovie.org",
      url='http://routes.readthedocs.org/',
      license="MIT",
      test_suite="nose.collector",
      include_package_data=True,
      zip_safe=False,
      tests_require=['nose', 'webtest', 'webob', 'coverage'],
      install_requires=[
          "repoze.lru>=0.3"
      ],
      **extra_options
)
