from setuptools import setup
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='superprocess',
    version='0.1.0',
    description='subprocess-like API for starting local and remote processes',
    long_description=long_description,

    url='https://bitbucket.org/sjdrake/superprocess',
    author='Stephen Drake',
    author_email='steve@synergyconsultingnz.com',

    license='Apache 2.0',

    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
    ],
    keywords='subprocess ssh',

    packages=['superprocess'],
)
