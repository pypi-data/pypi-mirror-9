from setuptools import setup

__VERSION__ = '0.1.5'

setup(
    name='json_resource_http',
    version=__VERSION__,
    packages=['json_resource_http'],
    long_description=open('./README.rst').read(),
    author='Ernst Odolphi',
    author_email='ernst.odolphi@gmail.com',
    install_requires=['json_resource', 'requests'],
    tests_require=['mock', 'nose'],
    test_suite='nose.collector'
)
