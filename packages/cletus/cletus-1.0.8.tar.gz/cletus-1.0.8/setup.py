#!/usr/bin/env python

import os, uuid
from pip.req import parse_requirements
from setuptools import setup, find_packages

def read(*paths):
    """Build a file path from *paths* and return the contents."""
    with open(os.path.join(*paths), 'r') as f:
        return f.read()

def get_version():
    v1_rec = read("cletus/_version.py")
    (v1_label, v1_version) = v1_rec.split('=')
    v2_version = v1_version.strip()[1:-1]
    assert v1_label.strip() == '__version__'
    assert v2_version.count('.') == 2
    return v2_version

VERSION          = get_version()
DESCRIPTION      = 'A library of command line utilities'
REQUIREMENTS     = [str(ir.req) for ir in parse_requirements('requirements.txt', session=uuid.uuid1())]

setup(name             = 'cletus'          ,
      version          = VERSION           ,
      description      = DESCRIPTION       ,
      long_description=(read('README.rst') + '\n\n' +
                        read('CHANGELOG.rst')),
      keywords         = "utility",
      author           = 'Ken Farmer'      ,
      author_email     = 'kenfar@gmail.com',
      url              = 'http://github.com/kenfar/cletus',
      license          = 'BSD'             ,
      classifiers=[
            'Development Status :: 4 - Beta'                         ,
            'Environment :: Console'                                 ,
            'Intended Audience :: Developers'                        ,
            'License :: OSI Approved :: BSD License'                 ,
            'Programming Language :: Python'                         ,
            'Operating System :: POSIX'                              ,
            'Topic :: Utilities'
            ],
      scripts          = ['scripts/cletus_archiver.py'],
      install_requires = REQUIREMENTS,
      packages         = find_packages(),
     )
