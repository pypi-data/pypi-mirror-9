'''
Created on Dec 3, 2013

@author: harsnara

@change:     2013-12-03    :    Initial Draft
             2013-12-09    :    Changes Made for release 0.0.2
             2013-12-13    :    Installation Script modified to support Static data that are being used for
                                report generation as templates.
             2014-03-12    :    New release to support Bug Fix.
             2014-07-16    :    New Release to Support Additional Logging and RegExp Support in Exemptions File. V 0.0.3.2
             2015-03-10    :    Test Suite Included to Run Tests during Installation time.
             2015-03-10    :    New Release. V 0.0.3.3
'''

__version__ = "0.0.5"
__author__ ="Harsha Narayana"
__date__ = "03 Dec 2013"

from setuptools import setup, find_packages

setup( name         = "deadcheck",
       version      = "0.0.3.3.1",
       description  = "Deadlink Check Utility using Python Modules",
       author       = "Harsha Narayana",
       author_email = "harsha2k4@gmail.com",
       url          = "https://github.com/harshanarayana/deadcheck",
       download_url = "https://github.com/harshanarayana/deadcheck",
       packages     = find_packages(),
       package_data = {'': ['Templates/*']},
       install_requires = ['lxml'],
       test_suite   = "t.test_suite",
       scripts      = ['run.py'],
       license      = "MIT",
       classifiers  = [
                        'Development Status :: 4 - Beta',
                        'Environment :: Console',
                        'Environment :: Web Environment',
                        'Environment :: Win32 (MS Windows)',
                        'Intended Audience :: Customer Service',
                        'Intended Audience :: Developers',
                        'Intended Audience :: Education',
                        'Intended Audience :: End Users/Desktop',
                        'Intended Audience :: Information Technology',
                        'Intended Audience :: System Administrators',
                        'License :: OSI Approved :: MIT License',
                        'License :: OSI Approved :: Python Software Foundation License',
                        'Operating System :: MacOS :: MacOS X',
                        'Operating System :: Microsoft',
                        'Operating System :: Microsoft :: MS-DOS',
                        'Operating System :: Microsoft :: Windows',
                        'Operating System :: Microsoft :: Windows :: Windows 7',
                        'Operating System :: OS Independent',
                        'Operating System :: POSIX',
                        'Programming Language :: Python',
                        'Programming Language :: Python :: 2.7',
                        'Topic :: Communications :: Email',
                        'Topic :: Internet',
                        'Topic :: Internet :: WWW/HTTP',
                        'Topic :: Internet :: WWW/HTTP :: Browsers',
                        'Topic :: Internet :: WWW/HTTP :: Dynamic Content :: Page Counters',
                        'Topic :: Office/Business',
                        'Topic :: Software Development :: Bug Tracking',
                        'Topic :: Software Development :: Libraries :: Python Modules',
                        'Topic :: Text Processing :: Markup :: HTML',
                       ],
    )