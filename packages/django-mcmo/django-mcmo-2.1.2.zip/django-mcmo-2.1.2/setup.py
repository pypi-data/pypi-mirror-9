"""
django-mcmo
Allows multiple apps to override the same management command in Django
(c) 2014 Thomas Khyn
MIT license (see LICENSE.txt)
"""

from setuptools import setup, find_packages
import os


# imports __version__ variable
exec(open('mcmo/version.py').read())
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
    name='django-mcmo',
    version=__version__,
    description='Allows multiple apps to override the same management ' \
                'command in Django',
    long_description=open(os.path.join('README.rst')).read(),
    author='Thomas Khyn',
    author_email='thomas@ksytek.com',
    url='https://bitbucket.org/tkhyn/django-mcmo',
    keywords=['django', 'management', 'multiple'],
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Development Status :: %s' % DEV_STATUS[dev_status],
        'Intended Audience :: Developers',
        'Framework :: Django',
        'Environment :: Other Environment',
        'Topic :: Software Development :: Libraries',
        'Topic :: Utilities'
    ],
    packages=find_packages(),
    install_requires=(
        'django>=1.4',
    ),
    zip_safe=False
)
