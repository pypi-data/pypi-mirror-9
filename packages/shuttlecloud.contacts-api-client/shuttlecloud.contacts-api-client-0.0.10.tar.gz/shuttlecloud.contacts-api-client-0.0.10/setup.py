from setuptools import setup
from glob import glob
import os


PACKAGE_VERSION = '0.0.10'
PACKAGE_NAME = 'shuttlecloud.contacts-api-client'


EXAMPLES_TARGET_DIR = 'share/{}/examples'.format(PACKAGE_NAME)
EXAMPLES_LOCAL_DIR = 'examples'
EXAMPLES = (
    'interactive_client',
)


def get_data_files():
    data_files = []

    for example in EXAMPLES:
        target_dir = os.path.join(EXAMPLES_TARGET_DIR, example)
        target_files = glob(os.path.join(EXAMPLES_LOCAL_DIR, example, '*'))
        data_files.append((target_dir, target_files))

    return data_files


setup(
    name=PACKAGE_NAME,
    author='ShuttleCloud Corp.',
    author_email='dev@shuttlecloud.com',
    description='ShuttleCloud Contacts API Official Python Client',
    url='http://github.com/shuttlecloud/contacts-api-client',
    version=PACKAGE_VERSION,
    packages=[
        'shuttlecloud',
        'shuttlecloud.contacts_api_client'
    ],
    include_package_data=True,
    zip_safe=False,
    namespace_packages=['shuttlecloud'],
    install_requires=[
        'requests'
    ],
    data_files=get_data_files(),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Programming Language :: Python :: 2',
    ],
)
