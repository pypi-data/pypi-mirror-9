import os
import sys

from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand


# Some initialization
APP_NAME = 'cmstemplates'
PROJECT_NAME = 'django-cmstemplates'
HERE = os.path.abspath(os.path.dirname(__file__))
LONG_DESCRIPTION = open(os.path.join(HERE, 'README.rst')).read()


data_files = []
root_dir = os.path.dirname(__file__)
if root_dir:
    os.chdir(root_dir)


# this code snippet is taken from django-registration setup.py script
for dirpath, dirnames, filenames in os.walk(APP_NAME):
    # Ignore dirnames that start with '.'
    for i, dirname in enumerate(dirnames):
        if dirname.startswith('.'):
            del dirnames[i]
    if filenames:
        # Strip "app_name/" or "app_name\"
        prefix = dirpath[len(APP_NAME)+1:]
        for f in filenames:
            data_files.append(os.path.join(prefix, f))

class Tox(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True
    def run_tests(self):
        #import here, cause outside the eggs aren't loaded
        import tox
        errcode = tox.cmdline(self.test_args)
        sys.exit(errcode)


setup(
    name=PROJECT_NAME,
    version="0.3.2",
    packages=find_packages(),
    author="asyncee",
    description="Efficient django template blocks implementation",
    long_description=LONG_DESCRIPTION,
    license="MIT",
    keywords="django cmstemplates",
    url='https://github.com/asyncee/django-cmstemplates',
    download_url='https://pypi.python.org/pypi/django-cmstemplates/',
    classifiers=[
          'Development Status :: 4 - Beta',
          'Environment :: Web Environment',
          'Framework :: Django',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: MIT License',
          'Programming Language :: Python',
          'Programming Language :: Python :: 2',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.3',
          'Programming Language :: Python :: 3.4',
          'Topic :: Internet :: WWW/HTTP :: Site Management',

    ],

    package_dir={'cmstemplates': 'cmstemplates'},
    package_data={'cmstemplates': data_files},
    zip_safe=False,
    extras_require={
        'codemirror': 'django-codemirror-widget==0.4.0',
    },
    tests_require=['tox'],
    cmdclass = {'test': Tox},
)
