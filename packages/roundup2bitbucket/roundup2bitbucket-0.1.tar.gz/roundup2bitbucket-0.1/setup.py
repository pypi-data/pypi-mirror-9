from distutils.core import setup

setup(
    name='roundup2bitbucket',
    version='0.1',
    scripts=['roundup2bitbucket.py'],
    url='https://bitbucket.org/takis/roundup2bitbucket',
    license='GPL',
    author='Takis Issaris',
    author_email='takis@issaris.org',
    description='Convert Roundup data to Bitbucket\'s issue tracker',
    long_description="""his program allows one to convert a Roundup issue tracker instance to Bitbucket's issue tracker.
Point it to the directory containing the database, and it will generate a ZIP-file which you can import from the
Bitbuckets issue tracker settings page.""",
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.4',
        'Topic :: Software Development :: Bug Tracking',
    ],
    keywords='development bitbucket roundup',
)
