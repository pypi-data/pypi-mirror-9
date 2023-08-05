import collections

from distutils.version import StrictVersion
from setuptools import setup, find_packages
from pip.req import parse_requirements
import pip

with open('README.md', 'r') as readme_fd:
    LONG_DESCRIPTION = readme_fd.read()


def get_install_requirements(fname):

    ReqOpts = collections.namedtuple('ReqOpts', [
        'skip_requirements_regex',
        'default_vcs',
        'isolated_mode',
    ])

    opts = ReqOpts(None, 'git', False)
    params = {'options': opts}

    requires = []
    dependency_links = []

    pip_version = StrictVersion(pip.__version__)
    session_support_since = StrictVersion('1.5.0')
    if pip_version >= session_support_since:
        from pip.download import PipSession
        session = PipSession()
        params.update({'session': session})

    for ir in parse_requirements(fname, **params):
        if ir is not None:
            if ir.url is not None:
                dependency_links.append(str(ir.url))
            if ir.req is not None:
                requires.append(str(ir.req))
        return requires, dependency_links


tests_require, _ = get_install_requirements('requirements-tests.txt')

setup(
    name='pyrehol',
    version='0.3',
    author='James Brown',
    author_email='jbrown@uber.com',
    url='https://github.com/uber/pyrehol',
    description='Python library for generating FireHOL config',
    license='MIT (Expat)',
    classifiers=[
        'Programming Language :: Python',
        'Operating System :: OS Independent',
        'Topic :: Security',
        'Intended Audience :: System Administrators',
        'Development Status :: 3 - Alpha',
        'Programming Language :: Python :: 2.7',
        'License :: OSI Approved :: MIT License',
    ],
    packages=find_packages(exclude=['tests']),
    tests_require=tests_require,
    test_suite='nose.collector',
    long_description=LONG_DESCRIPTION
)
