""" Setup file for distutils

"""

from distutils.core import setup
from setuptools import find_packages

NAME = 'pyonedrive'
GITHUB_ORG_URL = "https://github.com/cogniteev"
exec(open('pyonedrive/version.py').read())

setup(
    name=NAME,
    version=version,
    author='Tony Sanchez',
    author_email='mail.tsanchez@gmail.com',
    url=GITHUB_ORG_URL + NAME,
    download_url="{0}/{1}/tarball/v{2}".format(GITHUB_ORG_URL, NAME, version),
    description='Onedrive REST api client',
    packages=find_packages(exclude=['tests']),
    license='Apache license version 2.0',
    platforms='OS Independent',
    zip_safe=False,
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Environment :: Web Environment',
        'Development Status :: 4 - Beta'
    ],
    install_requires='requests>=2.2.1'
)
