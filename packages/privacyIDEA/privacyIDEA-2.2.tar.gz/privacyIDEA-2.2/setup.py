# -*- coding: utf-8 -*-
from setuptools import setup, find_packages
import os
import glob
import sys

#VERSION="2.1dev4"
VERSION="2.2"

# Taken from kennethreitz/requests/setup.py
package_directory = os.path.realpath(os.path.dirname(__file__))


def get_file_contents(file_path):
    """Get the context of the file using full path name."""
    content = ""
    try:
        full_path = os.path.join(package_directory, file_path)
        content = open(full_path, 'r').read()
    except:
        print >> sys.stderr, "### could not open file %r" % file_path
    return content


setup(
    name='privacyIDEA',
    version=VERSION,
    description='privacyIDEA: identity, multifactor authentication (OTP), '
                'authorization, audit',
    author='privacyidea.org',
    license='AGPLv3',
    author_email='cornelius@privacyidea.org',
    url='http://www.privacyidea.org',
    keywords='OTP, two factor authentication, management, security',
    packages=find_packages(),
    scripts=['pi-manage.py',
             'tools/privacyidea-convert-token',
             'tools/privacyidea-create-pwidresolver-user',
             'tools/privacyidea-create-sqlidresolver-user',
             'tools/privacyidea-pip-update',
             'tools/privacyidea-create-certificate',
             'tools/privacyidea-fix-access-rights',
             'tools/privacyidea-create-ad-users',
             'tools/privacyidea-fetchssh.sh'
             ],
    extras_require={
        'dev': ["Sphinx==1.2.3",
                "sphinxcontrib-httpdomain==1.3.0"],
        'test': ["coverage==3.7.1",
                 "mock==1.0.1",
                 "nose==1.3.4",
                 "responses==0.3.0",
                 "six==1.8.0"],
    },
    install_requires=["Flask==0.10.1",
                      "Flask-Cache==0.13.1",
                      "Flask-Migrate==1.2.0",
                      "Flask-SQLAlchemy==2.0",
                      "Flask-Script==2.0.5",
                      "Jinja2==2.7.3",
                      "Mako==1.0.0",
                      "MarkupSafe==0.23",
                      "MySQL-python==1.2.5",
                      "Pillow==2.6.1",
                      "PyJWT==0.3.0",
                      "PyYAML==3.11",
                      "Pygments==2.0.1",
                      "SQLAlchemy==0.9.8",
                      "Werkzeug==0.9.6",
                      "alembic==0.6.7",
                      "argparse==1.2.1",
                      "bcrypt==1.1.0",
                      "cffi==0.8.6",
                      "configobj==5.0.6",
                      "docutils==0.12",
                      "funcparserlib==0.3.6",
                      "itsdangerous==0.24",
                      "ldap3==0.9.7.2",
                      "netaddr==0.7.12",
                      "passlib==1.6.2",
                      "pyasn1==0.1.7",
                      "pycparser==2.10",
                      "pycrypto==2.6.1",
                      "pyrad==2.0",
                      "pyusb==1.0.0b2",
                      "qrcode==5.1",
                      "requests==2.5.0",
                      "sqlsoup==0.9.0",
                      "wsgiref==0.1.2"
    ],
    include_package_data=True,
    data_files=[('etc/privacyidea/',
                 ['deploy/apache/privacyideaapp.wsgi',
                  'tests/testdata/dictionary',
                  'deploy/privacyidea/enckey',
                  'deploy/privacyidea/private.pem',
                  'deploy/privacyidea/public.pem']),
                ('share/man/man1',
                 ["tools/privacyidea-convert-token.1",
                  "tools/privacyidea-create-pwidresolver-user.1",
                  "tools/privacyidea-create-sqlidresolver-user.1",
                  "tools/privacyidea-pip-update.1",
                  "tools/privacyidea-create-certificate.1",
                  "tools/privacyidea-fix-access-rights.1"
                  ]),
                ('lib/privacyidea/authmodules/FreeRADIUS',
                 ["authmodules/FreeRADIUS/LICENSE",
                  "authmodules/FreeRADIUS/privacyidea_radius.pm"]),
                ('lib/privacyidea/authmodules/OTRS',
                 ["authmodules/OTRS/privacyIDEA.pm"]),
                ('lib/privacyidea/migrations',
                 ["migrations/alembic.ini",
                  "migrations/env.py",
                  "migrations/README",
                  "migrations/script.py.mako"]),
                ('lib/privacyidea/migrations/versions',
                 ["migrations/versions/2551ee982544_.py",
                  "migrations/versions/4f32a4e1bf33_.py",
                  "migrations/versions/2181294eed0b_.py"])
                ],
    classifiers=["Framework :: Flask",
                 "License :: OSI Approved :: "
                 "GNU Affero General Public License v3",
                 "Programming Language :: Python",
                 "Development Status :: 5 - Production/Stable",
                 "Topic :: Internet",
                 "Topic :: Security",
                 "Topic :: System ::"
                 " Systems Administration :: Authentication/Directory"
                 ],
    #message_extractors={'privacyidea': [
    #        ('**.py', 'python', None),
    #        ('static/**.html', 'html', {'input_encoding': 'utf-8'})]},
    zip_safe=False,
    long_description=get_file_contents('README.md')
)
