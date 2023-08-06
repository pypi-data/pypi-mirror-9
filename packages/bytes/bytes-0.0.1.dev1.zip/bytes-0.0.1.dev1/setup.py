__author__ = 'code-museum'

from setuptools import setup

from bytes import __version__


REQUIREMENTS = []

setup(
    name='bytes',
    version=__version__,
    py_modules=['bytes'],
    packages=['_bytes'],
    install_requires=REQUIREMENTS,
    url='https://github.com/code-museum/bytes',
    license='GNU General Public License, version 2',
    author='code-museum',
    author_email='code-museum@users.noreply.github.com',
    description='Bytes: Serialization and deserialization utilities.',
    keywords="Serialization deserialization formats marshaling"
)