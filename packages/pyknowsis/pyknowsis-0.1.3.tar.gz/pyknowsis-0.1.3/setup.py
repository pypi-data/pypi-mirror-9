from setuptools import setup
from pyknowsis import __version__


setup(
    name='pyknowsis',
    include_package_data=True,
    version=__version__,
    packages=[
        'pyknowsis',
        'tests'
    ],
    description='API Wrapper for the Knowsis API',
    author='Knowsis Ltd',
    dependency_links=[],
    install_requires=['requests', 'simplejson', 'oauth2'],
    tests_require=[],
    url="https://github.com/knowsis/pyknowsis"
)
