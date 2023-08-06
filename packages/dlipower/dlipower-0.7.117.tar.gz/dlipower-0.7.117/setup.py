import json
import os
from setuptools import setup
import sys

METADATA_FILENAME = 'dlipower/package_metadata.json'
BASEPATH = os.path.dirname(os.path.abspath(__file__))


def readme():
    with open('README.rst') as f:
        return f.read()


class Git(object):
    version_list = ['0', '7', '0']

    def __init__(self, version=None):
        if version:
            self.version_list = version.split('.')

    @property
    def version(self):
        """
        Generate a Unique version value from the git information
        :return:
        """
        git_rev = len(os.popen('git rev-list HEAD').readlines())
        if git_rev != 0:
            self.version_list[-1] = '%d' % git_rev
        version = '.'.join(self.version_list)
        return version

    @property
    def branch(self):
        """
        Get the current git branch
        :return:
        """
        return os.popen('git rev-parse --abbrev-ref HEAD').read().strip()

    @property
    def hash(self):
        """
        Return the git hash for the current build
        :return:
        """
        return os.popen('git rev-parse HEAD').read().strip()

    @property
    def origin(self):
        """
        Return the fetch url for the git origin
        :return:
        """
        for item in os.popen('git remote -v'):
            split_item = item.strip().split()
            if split_item[0] == 'origin' and split_item[-1] == '(push)':
                return split_item[1]


def get_and_update_metadata():
    """
    Get the package metadata or generate it if missing
    :return:
    """
    if not os.path.exists('.git') and os.path.exists(METADATA_FILENAME):
        with open(METADATA_FILENAME) as fh:
            metadata = json.load(fh)
    else:
        git = Git()
        metadata = {
            'version': git.version,
            'git_hash': git.hash,
            'git_origin': git.origin,
            'git_branch': git.branch
        }
        with open(METADATA_FILENAME, 'w') as fh:
            json.dump(metadata, fh)
    return metadata


metadata = get_and_update_metadata()


requires = ['six']
if sys.version > '3.0.0':
    print('Python3')
    requires.append('BeautifulSoup4')
else:
    print('Python2')
    requires.append('BeautifulSoup')


print('Setting up under python version %s' % sys.version)
print('Requirements: %s' % ','.join(requires))

setup(
    name="dlipower",
    version=metadata['version'],
    author="Dwight Hubbard",
    author_email="dwight@dwighthubbard.com",
    url="https://github.com/dwighthubbard/python-dlipower/",
    license='License :: OSI Approved :: BSD License',
    packages=["dlipower", ],
    scripts=["dlipower/dlipower", "dlipower/fence_dli"],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Intended Audience :: Information Technology',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Operating System :: POSIX',
        'Operating System :: POSIX :: Linux',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: POSIX :: BSD :: FreeBSD',
        'Operating System :: POSIX :: SunOS/Solaris',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python',
        'Topic :: System :: Systems Administration',
        'Topic :: Utilities',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: System :: Hardware :: Hardware Drivers',
        'Topic :: System :: Power (UPS)',
    ],
    long_description=readme(),
    description="Control digital loggers web power switch",
    requires=requires,
    install_requires=requires,
    package_data={
        'dlipower': ['package_metadata.json']
    },
    include_package_data=True,
    zip_safe=True,
)
