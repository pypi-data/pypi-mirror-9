from setuptools import setup
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'DESCRIPTION.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='naive',
    version='0.0.3',
    description='A naive static site generator',
    long_description=long_description,
    url='https://github.com/ahnjungho/naive',
    author='Ahn Jungho',
    author_email='ahnjungho@ahnjungho.org',
    license='MIT',

    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
    ],

    keywords='static site generator',

    packages=['naive'],

    install_requires=['Markdown', 'Jinja2', 'libsass', 'PyYAML'],

    entry_points={
        'console_scripts': [
            'naive=naive:main',
        ],
    },


)
