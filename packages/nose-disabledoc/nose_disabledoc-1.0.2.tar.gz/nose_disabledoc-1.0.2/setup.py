
from setuptools import setup, find_packages

setup(
    name='nose_disabledoc',
    version='1.0.2',
    description="""Nose plugin that disables test docstrings in the verbose output and
    instead uses the test name (and path, if applicable)""",
    long_description="""""",
    author='Nat Williams, Kumar McMillan, Mark Hirota',
    author_email='sanseihappa@users.noreply.github.com',
    license="Apache License",
    packages=find_packages(exclude=['ez_setup']),
    install_requires=['nose'],
    url='https://github.com/sanseihappa/nose-disabledoc',
    include_package_data=True,
    entry_points="""
       [nose.plugins.0.10]
       nose_disabledoc = nose_disabledoc.plugin:DisableDocstring
       """,
    classifiers=[
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Topic :: Software Development :: Testing'
        ],
    )
