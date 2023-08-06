import os
import re
from setuptools import setup, find_packages

with open(os.path.join(os.path.dirname(__file__),
                       'webassets_react', '__init__.py')) as init_py:
    VERSION = re.search("__version__ = '([^']+)'", init_py.read()).group(1)

with open('README.rst') as readme_file:
    README = readme_file.read().strip()

PROJECT = README.strip('#').split('\n')[0].strip().split()[0].lower()
DESCRIPTION = "The webassets filter for transform React JSX to JS."

with open('requirements.txt') as reqs_file:
    REQS = reqs_file.read()

setup(
    name='webassets-react',
    version=VERSION,
    packages=find_packages(exclude=['tests']),
    install_requires=REQS,
    include_package_data=True,
    url='http://github.com/dotnetage/webassets-react',
    license='BSD',
    author='Ray',
    author_email='csharp2002@hotmail.com',
    description=DESCRIPTION,
    long_description=README,
    zip_safe=False,
    platforms='any',
    keywords=('webassets','react','jsx'),
    classifiers=['Development Status :: 5 - Production/Stable',
                 'Intended Audience :: Developers',
                 'License :: OSI Approved :: BSD License',
                 'Natural Language :: English',
                 'Operating System :: OS Independent',
                 'Programming Language :: Python :: 2.7',
                 'Topic :: Software Development :: Libraries',
                 'Topic :: Utilities']
)
