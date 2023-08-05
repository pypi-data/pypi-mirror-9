from setuptools import setup

__VERSION__ = '0.2.7'

setup(
    name='json_resource',
    version=__VERSION__,
    packages=['json_resource'],
    package_data={'json_resource': ['schemas/*.json']},
    long_description=open('./README.rst').read(),
    author='Ernst Odolphi',
    author_email='ernst.odolphi@gmail.com',
    install_requires=['json_pointer', 'jsonschema', 'json_patch', 'pymongo'],
    tests_require=['behave'],
)




