# -*- coding: utf-8 -*-
import glob
import os
import sys

from paver.easy import *  # noqa
try:
    import paver.doctools  # noqa
except ImportError:
    pass
from paver.setuputils import setup
sys.path.append('.')

with open('README.rst') as file:
    long_description = file.read()

setup(
    name='django-kidoredis',
    version='1.0.1',
    description='Django redis backend',
    long_description=long_description,
    url="http://kidosoft.pl",
    author="Jakub STOLARSKI (Dryobates)",
    author_email="jakub.stolarski@kidosoft.pl",
    license="beerware",
    keywords="django redis",
    packages=['kidoredis'],
    install_requires=[
        'redis',
        'hash_ring',
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Framework :: Django',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)

options(
    sphinx=Bunch(
        builddir="_build",
        apidir=None,
    )
)


@task
@needs('generate_setup', 'minilib', 'setuptools.command.sdist')
def sdist():
    """Overrides sdist to make sure that our setup.py is generated."""
    pass


@task
def cleanup():
    """ Removes generated files. """
    sh('rm -rf dist', ignore_error=True)
    sh('rm -rf build', ignore_error=True)
    sh('rm -rf *.egg-info', ignore_error=True)
    sh('rm -rf htmlcov', ignore_error=True)
    sh('rm -rf docs/_build', ignore_error=True)
    sh('rm setup.py', ignore_error=True)
    sh('rm paver-minilib.zip', ignore_error=True)


@task
def kwalitee(options):
    """ Removes generated files. """
    sh('flake8 %s' % ' '.join(options.packages), ignore_error=True)
    sh('pep257 %s' % ' '.join(options.packages), ignore_error=True)


@task
@task
@cmdopts([
    ("packages_dir=", "p", "Run tests with all Django versions found in directory"),
])
def coverage(options):
    """ Generages coverage reports. """
    omit = [
        'pavement.py',
        'manage.py',
        'setup.py',
        'example/*',
    ]
    omit = ','.join([repr(filename) for filename in omit])
    if getattr(options, 'packages_dir', False):
        sh('coverage erase')
        for filename in glob.glob(os.path.join(options.packages_dir, 'Django*')):
            sh('pip uninstall -q -y Django', ignore_error=True)
            sh('pip install -q -U %s' % filename)
            sh('coverage run --append --source . --omit %s manage.py test -v 0 %s' % (omit, ' '.join(options.packages)))
    else:
        sh('coverage run --source . --omit %s manage.py test -v 0 %s' % (omit, ' '.join(options.packages)))
    sh('coverage html')
    sh('coverage report --fail-under=100')


@task
@cmdopts([
    ("path=", "p", "Docs path"),
])
@needs('cleanup')
def publish_docs(options):
    """ Uploads docs to server. """
    try:
        call_task('html')
    except:
        pass
    sh('''sed -i '' 's/href="\(http:\/\/sphinx-doc.org\)/rel="nofollow" href="\\1"/' docs/_build/html/*.html''')
    sh('rsync -av docs/_build/html/ %s/%s/' % (options.path, options.name))
