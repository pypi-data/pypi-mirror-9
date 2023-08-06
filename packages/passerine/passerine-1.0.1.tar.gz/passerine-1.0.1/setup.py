try:
    from setuptools import setup
except:
    from distutils.core import setup

setup(
    name         = 'passerine',
    version      = '1.0.1',
    description  = 'A generic object relational mapper (ORM) and data abstraction layer (DAL) primarily designed for NoSQL databases.',
    license      = 'MIT',
    author       = 'Juti Noppornpitak',
    author_email = 'juti_n@yahoo.co.jp',
    url          = 'https://github.com/shiroyuki/passerine',
    packages     = [
        'passerine',
        'passerine.data',
        'passerine.db',
        'passerine.db.driver',
        'passerine.db.metadata',
        'passerine.decorator',
    ],
    classifiers   = [
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries',
        'Topic :: Database'
    ],
    install_requires = ['pymongo']
)
