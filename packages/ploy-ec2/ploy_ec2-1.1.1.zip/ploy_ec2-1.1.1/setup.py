from setuptools import setup
import os


here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.rst')).read()
HISTORY = open(os.path.join(here, 'HISTORY.rst')).read()


version = "1.1.1"


setup(
    version=version,
    description="Plugin for ploy to provision Amazon EC2 instances.",
    long_description=README + "\n\n" + HISTORY,
    name="ploy_ec2",
    author='Florian Schulze',
    author_email='florian.schulze@gmx.net',
    license="BSD 3-Clause License",
    url='http://github.com/ployground/ploy_ec2',
    classifiers=[
        'Environment :: Console',
        'Intended Audience :: System Administrators',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 2 :: Only',
        'Topic :: System :: Installation/Setup',
        'Topic :: System :: Systems Administration'],
    include_package_data=True,
    zip_safe=False,
    packages=['ploy_ec2'],
    install_requires=[
        'setuptools',
        'ploy >= 1.0.0, < 2dev',
        'boto >= 2.0',
        'lazy'],
    entry_points="""
        [ploy.plugins]
        ec2 = ploy_ec2:plugin
    """)
