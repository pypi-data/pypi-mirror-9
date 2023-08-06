# -*- coding: utf-8 -*-
"""setuptools installer for period."""

import os
import uuid

from pip.req import parse_requirements
from setuptools import find_packages
from setuptools import setup
from setuptools.command.build_py import build_py

# local imports
try:
    from build_scripts.version import get_git_version
except:
    pass

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.rst')).read()
NEWS = open(os.path.join(here, 'NEWS.rst')).read()

version = None
try:
    version = get_git_version()
except:
    pass

if version is None or not version:
    try:
        file_name = "period/RELEASE-VERSION"
        version_file = open(file_name, "r")
        try:
            version = version_file.readlines()[0]
            version = version.strip()
        except Exception:
            version = "0.0.0"
        finally:
            version_file.close()
    except IOError:
        version = "0.0.0"


class my_build_py(build_py):
    def run(self):
        # honor the --dry-run flag
        if not self.dry_run:
            target_dirs = []
            target_dirs.append(os.path.join(self.build_lib,
                                            'period'))
            target_dirs.append('period')
            # mkpath is a distutils helper to create directories
            for dir in target_dirs:
                self.mkpath(dir)

            try:
                for dir in target_dirs:
                    fobj = open(os.path.join(dir, 'RELEASE-VERSION'), 'w')
                    fobj.write(version)
                    fobj.close()
            except:
                pass

        # distutils uses old-style classes, so no super()
        build_py.run(self)

test_reqs_gen = parse_requirements("test-requirements.txt",
                                  session=uuid.uuid1())
reqs_gen = parse_requirements("requirements.txt",
                              session=uuid.uuid1())


setup(name='period',
      version=version,
      description="basic time period checking libary for Python",
      long_description=README + '\n\n' + NEWS,
      cmdclass={'build_py': my_build_py},
      classifiers=[
          "Development Status :: 2 - Pre-Alpha",
          "Intended Audience :: Developers",
          "License :: OSI Approved :: Artistic License",
          "Operating System :: POSIX :: Linux",
          "Programming Language :: Python",
          "Programming Language :: Python :: 2.7",
          "Programming Language :: Python :: 3.4",
          "Topic :: Software Development :: Libraries :: Python Modules", ],
      keywords='date time period',
      author='William S. Annis',
      author_email='',
      url='https://github.com/LinkCareServices/period',
      license='Artistic License 2.0',
      packages=find_packages(exclude=['ez_setup']),
      package_data={'': ['*.rst', ], },
      include_package_data=True,
      zip_safe=False,
      test_suite='nose.collector',
      tests_require=[str(ir.req) for ir in test_reqs_gen],
      install_requires=[str(ir.req) for ir in reqs_gen], )
