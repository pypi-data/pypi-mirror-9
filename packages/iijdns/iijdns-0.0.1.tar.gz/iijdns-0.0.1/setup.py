from setuptools import setup

classifiers = [
  'License :: OSI Approved :: MIT License',
  'Programming Language :: Python',
  'Topic :: Internet :: Name Service (DNS)',
  'Topic :: Software Development :: Libraries :: Python Modules'
]

setup(
    name = "iijdns",
    version = "0.0.1",
    packages=['iijdns'],
    author = "samuraitaiga",
    author_email = "samuraitaiga@gmail.com",
    description = ("python library(API wrapper) for IIJ DNS service"),
    keywords=['iij','dns'],
    classifiers=classifiers,
    license = "MIT",
    url = "https://github.com/samuraitaiga/python-iij-dns",
)

