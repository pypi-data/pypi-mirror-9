#!/usr/bin/env python

from distutils.core import setup
import codecs
import os

def readme():
    directory = os.path.dirname(os.path.join(
        os.getcwd(),
        __file__,
        ))
    return codecs.open(os.path.join(directory, "README.rst"), "r", "utf8").read()

setup(name = 'chval',
      version = '0.6.7',
      description = 'Wrapper for getmail, providing daemon mode and encrypted passwords.',
      author = 'Louis Paternault',
      author_email = 'spalax@gresille.org',
      url = 'http://forge.spalax.fr.eu.org/chval',
      requires = [
          "Crypto",
          "lockfile",
          "pexpect",
          ],
      scripts = ['chval'],
      packages = ['chval_core' ],
      package_dir = {'chval_core' : 'chval_core' },
      license = "GPLv3 or any later version",
      platforms = "GNU/Linux",
      data_files=[
          #('/usr/share/man/man1', ['chval.1']),
          #('/usr/share/man/man5', ['chvalrc.5']),
          ],
      long_description=readme(),
)
