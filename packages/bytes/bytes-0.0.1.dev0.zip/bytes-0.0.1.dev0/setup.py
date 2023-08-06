from setuptools import setup

REQUIREMENTS = []

setup(
    name='bytes',
    version='0.0.1.dev0',
    py_modules=['bytes'],
    install_requires=REQUIREMENTS,
    url='https://github.com/code-museum/bytes',
    license='GNU General Public License, version 2',
    author='code-museum',
    author_email='code-museum@users.noreply.github.com',
    description='Bytes: Serialization and deserialization utilities.',
    keywords="Serialization deserialization formats marshaling"
)