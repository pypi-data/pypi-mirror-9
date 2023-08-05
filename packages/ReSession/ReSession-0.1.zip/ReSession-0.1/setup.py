__author__ = 'Reza Safaeiyan'
from setuptools import setup

setup(
    name='ReSession',
    version='0.1',
    description='ReSession is a Redis-based session for Tornado framework.',
    url='https://github.com/ReS4/ReSession',
    author='Reza Safaeiyan',
    author_email='Reza_S4T4N@Yahoo.com',
    license='MIT',
    packages=['ReSession'],
    zip_safe=False,
    requires=['redis', 'tornado'],
    classifiers=[
        # As from https://pypi.python.org/pypi?:action=list_classifiers
        # 'Development Status :: 1 - Planning',
        # 'Development Status :: 2 - Pre-Alpha',
        # 'Development Status :: 3 - Alpha',
        'Development Status :: 4 - Beta',
        # 'Development Status :: 5 - Production/Stable',
        # 'Development Status :: 6 - Mature',
        # 'Development Status :: 7 - Inactive',
        'Intended Audience :: Developers',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: GNU General Public License v2 (GPLv2)',
        'Natural Language :: English',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX',
        'Operating System :: MacOS',
        'Operating System :: Unix',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Internet',
        'Topic :: Internet :: WWW/HTTP :: Session',
    ],

)