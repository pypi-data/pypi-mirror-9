from setuptools import setup
from setuptools import find_packages

setup(
    name='GeobricksDeployment',
    version='0.0.1',
    author='Simone Murzilli; Guido Barbaglia',
    author_email='geobrickspy@gmail.com',
    packages=find_packages(),
    license='LICENSE.txt',
    long_description=open('README.md').read(),
    description='Geobricks Deployment.',
    entry_points={
        'console_scripts': [
            'geobricksdeploy = geobricks_deployment.cli:main',
        ]
    },
    install_requires=[
        'argh'
    ],
    url='http://pypi.python.org/pypi/GeobricksDeployment/'
)
