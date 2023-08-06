"""
djinga
Unobtrusive jinja2 integration in Django
(c) 2014 Thomas Khyn
MIT license (see LICENSE.txt) unless otherwise stated in file header
"""

from setuptools import setup, find_packages
import os


# imports __version__ variable
exec(open('djinga/version.py').read())
dev_status = __version_info__[3]

if dev_status == 'alpha' and not __version_info__[4]:
    dev_status = 'pre'

DEV_STATUS = {'pre': '2 - Pre-Alpha',
              'alpha': '3 - Alpha',
              'beta': '4 - Beta',
              'rc': '4 - Beta',
              'final': '5 - Production/Stable'}

# setup function parameters
setup(
    name='djinga',
    version=__version__,
    description='Unobtrusive jinja2 integration in Django',
    long_description=open(os.path.join('README.rst')).read(),
    author='Thomas Khyn',
    author_email='thomas@ksytek.com',
    url='https://bitbucket.org/tkhyn/djinga',
    keywords=['django', 'jinja2'],
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'License :: OSI Approved :: MIT License',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Development Status :: %s' % DEV_STATUS[dev_status],
        'Intended Audience :: Developers',
        'Framework :: Django',
        'Environment :: Other Environment',
        'Topic :: Software Development',
        'Topic :: Text Editors :: Text Processing',
    ],
    packages=find_packages(exclude=('tests',)),
    install_requires=(
      'django>=1.4',
      'jinja2',
    ),
    zip_safe=True,
)
