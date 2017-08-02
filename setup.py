import os
import os.path
import subprocess
from distutils.core import setup

git_version = 'UNKNOWN'
try:
    git_version = str(subprocess.check_output(['git', 'rev-parse', '--verify', '--short', 'HEAD'])).strip()
except subprocess.CalledProcessError as e:
    # print "Got error when trying to read git version: %s" % e
    pass

setup(
    name='gpmf',
    version='0.0.1dev-%s' % git_version,
    # version='0.6.6',
    author='Eero "rambo" af Heurlin',
    author_email='rambo@iki.fi',
    packages=['gpmf', ],
    license='MIT',
    long_description=open('README.md').read(),
    description='GoPro Metadata Format parser',
    install_requires=open(os.path.join(os.path.dirname(__file__), 'requirements.txt'), 'rt').readlines(),
    url='https://github.com/rambo/python-gpmf',
)
