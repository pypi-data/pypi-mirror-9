from distutils.core import setup


setup(
    name='cpsms',
    packages=['cpsms'],
    version='0.1',
    author='Mikkel Munch Mortensen',
    author_email='3xm@detfalskested.dk',
    url='https://github.com/decibyte/cpsms',
    description='A Python wrapper around the SMS gateway ' \
        'from CPSMS <https://www.cpsms.dk/>.',
    classifiers = [
        'Programming Language :: Python',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: OS Independent',
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Communications :: Telephony',
    ]
)
