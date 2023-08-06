#!/usr/local/bin/python

""" Configuration for the eGenix mxODBC product.

    Copyright (c) 1997-2000, Marc-Andre Lemburg; mailto:mal@lemburg.com
    Copyright (c) 2000-2015, eGenix.com Software GmbH; mailto:info@egenix.com
    See the documentation for further information on copyrights,
    or contact the author. All Rights Reserved.
    
"""
from mxSetup import mx_Extension, mx_version, platform_tags
import sys, os

#
# Package version
#
version = mx_version(3, 3, 2)

#
# Setup information
#
name = "egenix-mxodbc"

#
# Meta-Data
#
description = "eGenix mxODBC - ODBC Database Interface for Python"
long_description = """\
eGenix mxODBC - ODBC Database Interface for Python
--------------------------------------------------

The mxODBC Database Interface for Python is a commercial add-on to our
open-source eGenix mx Extension Series, providing robust and proven
database access for Python on all major platforms, such as Windows,
Linux, Mac OS X, FreeBSD, Solaris, using a single API acress all
platforms.

mxODBC provides an easy to use, high-performance, reliable and robust
Python interface to ODBC compatible databases such as MS SQL Server
and MS Access, Oracle Database, IBM DB2 and Informix , Sybase ASE and
Sybase Anywhere, MySQL, PostgreSQL, SAP MaxDB and many more. It is an
extension to our eGenix.com mx Base Distribution.

ODBC refers to Open Database Connectivity and is the industry standard
API for connecting applications to databases. In order to facilitate
setting up ODBC connectivity, operating systems typically provide ODBC
Managers which help set up the ODBC drivers and manage the binding of
the applications against these drivers.

On Windows the ODBC Data Source Manager is built into the system. On
Mac OS X, the iODBC ODBC manager is part of the the OS, with an
optional ODBC manager GUI available as separate download. On Unix
platforms, you can choose one of the ODBC managers unixODBC, iODBC or
DataDirect, which provide the same ODBC functionality on most Unix
systems.

mxODBC works with Python 2.4 - 2.7 and supports 32-bit as well as
64-bit platforms.

Downloads
---------

For downloads, documentation, installation instructions, changelog,
and feature list, please visit the product page at:

    http://www.egenix.com/products/python/mxODBC/

Web Installer
-------------

The source package on the Python Package Index (PyPI) is a web
installer, which will automatically select and download the right
binary for your installation platform.

Licenses
--------

For evaluation and production licenses, please visit our product
page at:

    http://www.egenix.com/products/python/mxODBC/#Licensing

This software is brought to you by eGenix.com and distributed under
the eGenix.com Commercial License 1.3.0.
"""
license = (
"eGenix.com Commercial License 1.3.0; "
"Copyright (c) 1997-2000, Marc-Andre Lemburg, All Rights Reserved; "
"Copyright (c) 2000-2015, eGenix.com Software GmbH, All Rights Reserved"
)
author = "eGenix.com GmbH"
author_email = "info@egenix.com"
maintainer = "eGenix.com GmbH"
maintainer_email = "info@egenix.com"
url = "http://www.egenix.com/products/python/mxODBC/"
download_url = 'https://downloads.egenix.com/python/download_url/%s/%s/' % (
    name,
    version)
platforms = [
    'Windows',
    'Linux',
    'FreeBSD',
    'Solaris',
    'Mac OS X',
    'AIX',
    ]
classifiers = [
    "Environment :: Console",
    "Environment :: No Input/Output (Daemon)",
    "Intended Audience :: Developers",
    "License :: Other/Proprietary License",
    "Natural Language :: English",
    "Operating System :: OS Independent",
    "Operating System :: Microsoft :: Windows",
    "Operating System :: POSIX",
    "Operating System :: Unix",
    "Operating System :: MacOS",
    "Operating System :: Other OS",
    "Programming Language :: C",
    "Programming Language :: Python",
    "Programming Language :: Python :: 2",
    "Programming Language :: Python :: 2.4",
    "Programming Language :: Python :: 2.5",
    "Programming Language :: Python :: 2.6",
    "Programming Language :: Python :: 2.7",
    "Topic :: Communications",
    "Topic :: Database",
    "Topic :: Database :: Database Engines/Servers",
    "Topic :: Database :: Front-Ends",
    "Topic :: Documentation",
    "Topic :: Internet",
    "Topic :: Office/Business",
    "Topic :: Software Development",
    "Topic :: Software Development :: Libraries",
    "Topic :: Software Development :: Libraries :: Application Frameworks",
    "Topic :: Software Development :: Libraries :: Python Modules",
    "Topic :: Utilities ",
    ]
if 'a' in version:
    classifiers.append("Development Status :: 3 - Alpha")
elif 'b' in version:
    classifiers.append("Development Status :: 4 - Beta")
else:
    classifiers.append("Development Status :: 5 - Production/Stable")
    classifiers.append("Development Status :: 6 - Mature")
classifiers.sort()

#
# Dependencies
#
if sys.version[:3] >= '2.5':
    # mxODBC extends egenix-mx-base; Note: the package name has to be
    # given using underscores, since setuptools doesn't like hyphens
    # in package names.
    requires = ['egenix_mx_base']

#
# Pure Python modules
#
packages = ['mx.ODBC',
            'mx.ODBC.Misc',
            'mx.ODBC.Manager']

#
# Data files
#
data_files = [

    'mx/ODBC/Doc/mxODBC.pdf',

    'mx/ODBC/COPYRIGHT',
    'mx/ODBC/LICENSE',
    'mx/ODBC/README',

]


#
# C Extension Packages (these extend packages and data_files as needed)
#

# Determine whether this is a 32- or 64-bit platform (this is
# important for some ODBC driver library names)
if sys.maxint > 2147483647L:
    _bits = '64'
else:
    _bits = '32'

# Setup common define_macros list
_common_defines = []

# Add defines from the license settings module, if available
try:
    import egenix_mxodbc_license_settings
except ImportError:
    pass
else:
    _common_defines.extend(
        egenix_mxodbc_license_settings.get_license_defines())

ext_modules = []

if sys.platform[:3] == 'win' or sys.platform == 'cygwin':
    ext_modules.extend([

        #
        # On Windows, we currently only build against the MS ODBC driver
        # manager.
        #
        # This could be extended to build directly against e.g. the MS
        # SQL Server Native Client or other ODBC drivers that provide
        # extended ODBC APIs.
        #
        
        mx_Extension('mx.ODBC.Windows.mxODBC',
                     ['mx/ODBC/Windows/mxODBC.c',
                      'mx/ODBC/Windows/mxSQLCodes.c'],
                     include_dirs=['mx/ODBC/Windows'],
                     define_macros=[('MS_ODBC_MANAGER', None),
                                    ('WANT_UNICODE_SUPPORT', None)]
                                   + _common_defines,
                     libraries=['odbc32'],
                     data_files=['mx/ODBC/Windows/COPYRIGHT',
                                 'mx/ODBC/Windows/LICENSE',
                                 'mx/ODBC/Windows/README'],
                     packages=['mx.ODBC.Windows'],
                     required=1
                     ),

        ])
else:
    _platform_tags = platform_tags()

    ext_modules.extend([

        #
        # These are the C extensions for the subpackages which the
        # installer will install.  If you want to disable installing
        # one of the default subpackages or would like to add a new
        # subpackage, edit this list accordingly.
        #
        # Note that mxSetup will try to auto-configure these sub-packages,
        # so disabling the various mx_Extension() definitions will usually
        # not be needed.
        #

        # iODBC 3.52.x manager (required)
        mx_Extension('mx.ODBC.iODBC.mxODBC',
                     ['mx/ODBC/iODBC/mxODBC.c',
                      'mx/ODBC/iODBC/mxSQLCodes.c'],
                     include_dirs=['mx/ODBC/iODBC'],
                     define_macros=[('iODBC', None),
                                    ('WANT_UNICODE_SUPPORT', None)]
                                   + _common_defines,
                     needed_includes=[('sql.h',
                                       ['/usr/local/iODBC/include',
                                        '/usr/local/iodbc/include'],
                                       'iODBC driver manager')],
                     needed_libraries=[('iodbc',
                                        ['/usr/local/iODBC/lib',
                                         '/usr/local/iodbc/lib'],
                                        '\[iODBC\]')],
                     data_files=['mx/ODBC/iODBC/COPYRIGHT',
                                 'mx/ODBC/iODBC/LICENSE',
                                 'mx/ODBC/iODBC/README'],
                     packages=['mx.ODBC.iODBC'],
                     required=1,
                     ),
        
        # unixODBC 2.2.x manager (required)
        mx_Extension('mx.ODBC.unixODBC.mxODBC',
                     ['mx/ODBC/unixODBC/mxODBC.c',
                      'mx/ODBC/unixODBC/mxSQLCodes.c'],
                     include_dirs=['mx/ODBC/unixODBC'],
                     define_macros=[('unixODBC', None),
                                    ('WANT_UNICODE_SUPPORT', None)]
                                   + _common_defines,
                     needed_includes=[('sql.h',
                                       ['/usr/local/unixODBC/include',
                                        '/usr/local/unixodbc/include'],
                                       'consistent with the MS version')],
                     needed_libraries=[('odbc',
                                        ['/usr/local/unixODBC/lib',
                                        '/usr/local/unixodbc/lib'],
                                        '\[unixODBC\]')],
                     data_files=['mx/ODBC/unixODBC/COPYRIGHT',
                                 'mx/ODBC/unixODBC/LICENSE',
                                 'mx/ODBC/unixODBC/README'],
                     packages=['mx.ODBC.unixODBC'],
                     required=1,
                     ),

        # DataDirect 5.1.x manager (required on Linux x86 and x64)
        mx_Extension('mx.ODBC.DataDirect.mxODBC',
                     ['mx/ODBC/DataDirect/mxODBC.c',
                      'mx/ODBC/DataDirect/mxSQLCodes.c'],
                     include_dirs=['mx/ODBC/DataDirect'],
                     define_macros=[('DataDirect', None),
                                    ('WANT_UNICODE_SUPPORT', None)]
                                   + _common_defines,
                     needed_includes=[('sql.h',
                                       ['/opt/odbc%sv71/include' % _bits,
                                        ],
                                       'DataDirect Technologies|Progress Software')],
                     needed_libraries=[('odbc',
                                        ['/opt/odbc%sv71/lib' % _bits,
                                         ],
                                        '\[DataDirect\]')],
                     data_files=['mx/ODBC/DataDirect/COPYRIGHT',
                                 'mx/ODBC/DataDirect/LICENSE',
                                 'mx/ODBC/DataDirect/README'],
                     packages=['mx.ODBC.DataDirect'],
                     required=('linux' in _platform_tags
                               and ('x86' in _platform_tags or
                                    'x64' in _platform_tags)),
                     warn=0,
                     ),

        ### These are optional subpackages

        # FreeTDS 0.82 driver (compiled against unixODBC or iODBC)
        mx_Extension('mx.ODBC.FreeTDS.mxODBC',
                     ['mx/ODBC/FreeTDS/mxODBC.c',
                      'mx/ODBC/FreeTDS/mxSQLCodes.c'],
                     include_dirs=['mx/ODBC/FreeTDS'],
                     define_macros=[('FreeTDS', None)]
                                   + _common_defines,
                     needed_includes=[('sql.h',
                                       ['/usr/local/unixODBC/include',
                                        '/usr/local/unixodbc/include',
                                        '/usr/local/iODBC/include',
                                        '/usr/local/iodbc/include'],
                                       'consistent with the MS version|'
                                       'iODBC driver manager')],
                     needed_libraries=[('tdsodbc',
                                        ['/usr/local/FreeTDS/lib',
                                         '/usr/local/freetds/lib'],
                                        'tds_connect')],
                     data_files=['mx/ODBC/FreeTDS/COPYRIGHT',
                                 'mx/ODBC/FreeTDS/LICENSE',
                                 'mx/ODBC/FreeTDS/README'],
                     packages=['mx.ODBC.FreeTDS'],
                     required=0,
                     warn=0,
                     ),

        # SAP DB 7.4.0.x ODBC driver
        mx_Extension('mx.ODBC.SAPDB.mxODBC',
                     ['mx/ODBC/SAPDB/mxODBC.c',
                      'mx/ODBC/SAPDB/mxSQLCodes.c'],
                     include_dirs=['mx/ODBC/SAPDB'],
                     define_macros=[('SAPDB', None)]
                                   + _common_defines,
                     needed_includes=[('sql.h',
                                       ['/opt/sapdb/indep_prog/incl'],
                                       '__SQL_SAPDB')],
                     needed_libraries=[('sqlod',
                                        ['/opt/sapdb/indep_prog/lib'],
                                        '\[SAP DB\]')],
                     data_files=['mx/ODBC/SAPDB/COPYRIGHT',
                                 'mx/ODBC/SAPDB/LICENSE',
                                 'mx/ODBC/SAPDB/README'],
                     packages=['mx.ODBC.SAPDB'],
                     required=0,
                     warn=0,
                     ),

        # IBM DB2 7.1 ODBC driver
        mx_Extension('mx.ODBC.DB2.mxODBC',
                     ['mx/ODBC/DB2/mxODBC.c',
                      'mx/ODBC/DB2/mxSQLCodes.c'],
                     include_dirs=['mx/ODBC/DB2'],
                     define_macros=[('IBMDB2', None),
                                    ('DONT_USE_SQLEXECDIRECT', None)]
                                   + _common_defines,
                     needed_includes=[('sql.h',
                                       ['/usr/IBMdb2/V7.1/include',
                                        '/opt/IBMdb2/V7.1/include'],
                                       'International Business Machines')],
                     needed_libraries=[('db2',
                                        ['/usr/IBMdb2/V7.1/lib',
                                         '/opt/IBMdb2/V7.1/lib'],
                                        '\[IBM\]')],
                     data_files=['mx/ODBC/DB2/COPYRIGHT',
                                 'mx/ODBC/DB2/LICENSE',
                                 'mx/ODBC/DB2/README'],
                     packages=['mx.ODBC.DB2'],
                     required=0,
                     warn=0,
                     ),
        
        # IBM DB2 9.1 ODBC driver
        mx_Extension('mx.ODBC.DB2.mxODBC',
                     ['mx/ODBC/DB2/mxODBC.c',
                      'mx/ODBC/DB2/mxSQLCodes.c'],
                     include_dirs=['mx/ODBC/DB2'],
                     define_macros=[('IBMDB2', None)]
                                   + _common_defines,
                     needed_includes=[('sql.h',
                                       ['/opt/ibm/db2/V9.1/include'],
                                       'International Business Machines')],
                     needed_libraries=[('db2',
                                        ['/opt/ibm/db2/V9.1/lib' + _bits],
                                        'db2cli')],
                     data_files=['mx/ODBC/DB2/COPYRIGHT',
                                 'mx/ODBC/DB2/LICENSE',
                                 'mx/ODBC/DB2/README'],
                     packages=['mx.ODBC.DB2'],
                     required=0,
                     warn=0,
                     ),
        
        # Solid 3.52 ODBC driver
        mx_Extension('mx.ODBC.Solid.mxODBC',
                     ['mx/ODBC/Solid/mxODBC.c',
                      'mx/ODBC/Solid/mxSQLCodes.c'],
                     include_dirs=['mx/ODBC/Solid'],
                     define_macros=[('SolidSDK', None)]
                                   + _common_defines,
                     needed_includes=[('sqlunix.h',
                                       ['/usr/local/solidSDKe352/Linux_glibc2/include',
                                        '/opt/solidSDKe352/Linux_glibc2/include'],
                                       'Solid Information Technology')],
                     needed_libraries=[('solodbc',
                                        ['/usr/local/solidSDKe352/Linux_glibc2/lib',
                                         '/opt/solidSDKe352/Linux_glibc2/lib'],
                                        'Solid ODBC')],
                     data_files=['mx/ODBC/Solid/COPYRIGHT',
                                 'mx/ODBC/Solid/LICENSE',
                                 'mx/ODBC/Solid/README'],
                     packages=['mx.ODBC.Solid'],
                     required=0,
                     warn=0,
                     ),

        # PostgreSQL 7.2.1 ODBC driver (compiled against iODBC)
        mx_Extension('mx.ODBC.PostgreSQL.mxODBC',
                     ['mx/ODBC/PostgreSQL/mxODBC.c',
                      'mx/ODBC/PostgreSQL/mxSQLCodes.c'],
                     include_dirs=['mx/ODBC/PostgreSQL'],
                     define_macros=[('PostgreSQL', None),
                                    ('DONT_HAVE_SQLDescribeParam', 1),]
                                   + _common_defines,
                     needed_includes=[('sql.h',
                                       ['/usr/local/iODBC/include',
                                        '/usr/local/iodbc/include'],
                                       'iODBC driver manager')],
                     needed_libraries=[('psqlodbc',
                                        ['/usr/local/pgsql/lib'],
                                        'PostgreSQL')],
                     data_files=['mx/ODBC/PostgreSQL/COPYRIGHT',
                                 'mx/ODBC/PostgreSQL/LICENSE',
                                 'mx/ODBC/PostgreSQL/README'],
                     packages=['mx.ODBC.PostgreSQL'],
                     required=0,
                     warn=0,
                     ),
        
        # MySQL 2.50.39 ODBC driver (compiled against iODBC 3.0.6)
        mx_Extension('mx.ODBC.MySQL.mxODBC',
                     ['mx/ODBC/MySQL/mxODBC.c',
                      'mx/ODBC/MySQL/mxSQLCodes.c'],
                     include_dirs=['mx/ODBC/MySQL'],
                     define_macros=[('MySQL', None)]
                                   + _common_defines,
                     needed_includes=[('sql.h',
                                       ['/usr/local/iODBC/include',
                                        '/usr/local/iodbc/include'],
                                       'iODBC driver manager')],
                     needed_libraries=[('myodbc',
                                        ['/usr/local/MyODBC/lib',
                                         '/usr/local/mysql/lib',
                                         '/usr/lib/mysql'],
                                        '\[MyODBC\]'),
                                       ('mysqlclient',
                                        ['/usr/local/MySQL/lib',
                                         '/usr/local/mysql/lib',
                                         '/usr/lib/mysql'],
                                        'mysql_connect'),
                                       ],
                     data_files=['mx/ODBC/MySQL/COPYRIGHT',
                                 'mx/ODBC/MySQL/LICENSE',
                                 'mx/ODBC/MySQL/README'],
                     packages=['mx.ODBC.MySQL'],
                     required=0,
                     warn=0,
                     ),
        
        # EasySoft 1.4.0 ODBC-ODBC bridge client (multi-threaded)
        mx_Extension('mx.ODBC.EasySoft.mxODBC',
                     ['mx/ODBC/EasySoft/mxODBC.c',
                      'mx/ODBC/EasySoft/mxSQLCodes.c'],
                     include_dirs=['mx/ODBC/EasySoft'],
                     define_macros=[('EasySoft', None),
                                    #('DONT_HAVE_SQLDescribeParam', 1),
                                    ('WANT_UNICODE_SUPPORT', None)
                                    ]
                                   + _common_defines,
                     needed_includes=[('sql.h',
                                       ['/usr/local/easysoft/oob/client/include'],
                                       'Microsoft')],
                     needed_libraries=[('esoobclient_r',
                                        ['/usr/local/easysoft/oob/client'],
                                        'oob_SQLDriverConnect')],
                     data_files=['mx/ODBC/EasySoft/COPYRIGHT',
                                 'mx/ODBC/EasySoft/LICENSE',
                                 'mx/ODBC/EasySoft/README'],
                     packages=['mx.ODBC.EasySoft'],
                     required=0,
                     warn=0,
                     ),
        
        #
        # Example:
        #
        # You should use the information from the Setup file in the
        # subpackage directory to modify the mx_Extension() entry as needed.
        #
#        mx_Extension('mx.ODBC.Adabas.mxODBC',
#                     ['mx/ODBC/Adabas/mxODBC.c',
#                     'mx/ODBC/Adabas/mxSQLCodes.c'],
#                     include_dirs=['mx/ODBC/Adabas',
#                                  '/usr/lib/adabase/incl'],
#                     define_macros=[('Adabas', None)]
#                                   + _common_defines,
#                     library_dirs=['/usr/lib/adabas'],
#                     libraries=['odbc', 'sqlrte', 'sqlptc'],
#                     required=0,
#                     warn=0,
#                     ),

        ])

# Declare namespace packages (for building eggs)
namespace_packages = [
    'mx',
    ]
        
