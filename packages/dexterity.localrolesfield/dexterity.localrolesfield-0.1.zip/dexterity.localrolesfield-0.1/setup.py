from setuptools import setup, find_packages

version = '0.1'

long_description = (
    open('README.rst').read()
    + '\n' +
    'Contributors\n'
    '============\n'
    + '\n' +
    open('CONTRIBUTORS.rst').read()
    + '\n' +
    open('CHANGES.rst').read()
    + '\n')

setup(
    name='dexterity.localrolesfield',
    version=version,
    description="z3c.form local role field for dexterity",
    long_description=long_description,
    # Get more strings from
    # http://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        "Environment :: Web Environment",
        "Framework :: Plone",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    keywords='',
    author='IMIO',
    author_email='support@imio.be',
    url='https://github.com/collective/',
    license='gpl',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    namespace_packages=['dexterity', ],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'Products.CMFCore',
        'collective.z3cform.datagridfield',
        'dexterity.localroles',
        'five.grok',
        'plone.api',
        'plone.app.dexterity',
        'setuptools',
    ],
    extras_require={
        'test': [
            'plone.app.testing',
            'plone.app.robotframework',
        ],
    },
    entry_points="""
    # -*- Entry points: -*-
    """,
)
