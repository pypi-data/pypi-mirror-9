from setuptools import setup

classifiers = [
  'License :: OSI Approved :: MIT License',
  'Programming Language :: Python',
  'Topic :: Internet :: Name Service (DNS)',
  'Topic :: Software Development :: Libraries :: Python Modules'
]

setup(
    name = "iijdns",
    version = "0.0.2",
    packages=['iijdns'],
    author = "samuraitaiga",
    author_email = "samuraitaiga@gmail.com",
    description = ("python library(API wrapper) for IIJ DNS service"),
    keywords=['iij','dns'],
    classifiers=classifiers,
    license = "MIT",
    install_requires = ['PyYAML==3.11', 'urllib3==1.10'],
    url = "https://github.com/samuraitaiga/python-iij-dns",
)

