from setuptools import setup
import os

def readme():
    with open( os.path.dirname(os.path.abspath(__file__)) + '/README.rst') as f:
        return f.read()

setup(
    name='jiraorm',
    version='0.1',
    description='Object oriented wrapper around JIRA.',
    long_description=readme(),
    url='git@github.com/Diplomat14/jiraorm',
    author='Aleksey Denysyuk',
    author_email='diplomt@gmail.com',
    license='MIT', #TBD
    packages=['jiraorm'],
    install_requires=[
        'jira',
        'xdev @ git+http://git@github.com/Diplomat14/xdev.git'
        ],
    #dependency_links=['http://server/user/repo/tarball/master#egg=package-1.0'],
    entry_points = {
        'console_scripts':['jiraorm-main=jiraorm.console.command_line:main']
    },
    include_package_data=True,
    test_suite='nose.collector',
    tests_require=['nose'],
    zip_safe=False
)