from setuptools import setup

setup(
    name='seymour',
    version='0.5',
    packages=['seymour'],
    install_requires=['Selenium>=2.25', 'argparse>=1.2.1'],
    author='L. Brouwer',
    author_email='objectified@gmail.com',
    maintainer='L. Brouwer',
    maintainer_email='objectified@gmail.com',
    description='Selenium RC to Nagios library',
    long_description='''
        This Python module provides the base dependency for tests that can be created using Selenium IDE
        and exported from there using the Seymour formatter. These exported tests depend on this Seymour
        module, and can then be run as Nagios NRPE scripts against Selenium RC servers. The script will
        produce sensible Nagios output such as performance data, correct status codes, test result details etc.''',
    license='Apache License, 2.0',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: System Administrators',
        'Programming Language :: Python',
    ],
)
