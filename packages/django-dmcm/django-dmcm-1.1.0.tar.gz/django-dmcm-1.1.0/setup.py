import os
from setuptools import setup

import dmcm

version = dmcm.__version__
long_description = open(os.path.join(os.path.dirname(__file__), 'README.rst')).read()

setup(
    name = 'django-dmcm',
    version = version,
    packages = ['dmcm'],
    include_package_data = True,
    license = 'BSD License',
    description = 'Django Markdown Content Manager.',
    long_description = long_description,
    url = 'https://github.com/ahernp/DMCM',
    author = 'Paul Ahern',
    author_email = 'ahernp@ahernp.com',
    classifiers = [
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
    install_requires=[
        'Django==1.8',
        'django-braces==1.4.0',
        'Markdown==2.6.1',
        'factory-boy==2.5.1',
    ],
)
