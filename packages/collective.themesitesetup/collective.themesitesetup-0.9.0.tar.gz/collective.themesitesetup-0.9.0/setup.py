from setuptools import setup, find_packages

setup(
    name='collective.themesitesetup',
    version='0.9.0',
    description='GenericSetup profiles for plone.app.theming',
    long_description=(open('README.rst').read() + '\n' +
                      open('CHANGES.rst').read()),
    # Get more strings from
    # http://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Plone :: 4.1',
        'Framework :: Plone :: 4.2',
        'Framework :: Plone :: 4.3',
    ],
    keywords='',
    author='Asko Soukka',
    author_email='asko.soukka@iki.fi',
    url='https://github.com/collective/collective.themesitesetup/',
    license='GPL',
    packages=find_packages('src', exclude=['ez_setup']),
    package_dir={'': 'src'},
    namespace_packages=['collective'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'Products.GenericSetup',
        'plone.api',
        'plone.app.controlpanel',
        'plone.app.theming',
        'plone.autoform',
        'plone.supermodel',
        'plone.z3cform',
        'setuptools',
        'z3c.form',
        'zope.schema',
    ],
    extras_require={'test': [
        'plone.app.testing',
        'plone.app.robotframework',
        'robotframework-selenium2screenshots',
    ]},
    entry_points="""
    # -*- Entry points: -*-
    [z3c.autoinclude.plugin]
    target = plone
    """
)
