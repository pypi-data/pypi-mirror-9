import os
from setuptools import setup, find_packages


def get_readme():
    try:
        return open(os.path.join(os.path.dirname(__file__), 'README.md')).read()
    except IOError:
        return ''

setup(
    name='securitylib',
    version='1.0.2',
    packages=find_packages(),
    install_requires=[
        'pycrypto>=2.6.1',
    ],
    package_data={
        '': ['*.txt', '*.md'],
    },

    author='Hugo Peres Castilho',
    author_email='hugo.p.castilho@telecom.pt',
    url='http://oss.sapo.pt/securitylib-python/',
    description=('The SAPO Security Lib is a library whose purpose is to '
        'provide functions/classes that solve common security related problems,'
        ' while being easy to use even by those who are not security experts.'),
    long_description = get_readme(),
    license='MIT',
    keywords=['security', 'crypto', 'securitylib'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: MIT License',
        'Intended Audience :: Developers',
        'Operating System :: Unix',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: MacOS :: MacOS X',
        'Programming Language :: Python :: 2',
        'Topic :: Security :: Cryptography',
        ],
)
