from setuptools import setup, find_packages
import os

name = 'seantis.people'
description = (
    "A list of people, optionally organized by organizations and positions."
)
version = '0.30'

tests_require = [
    'plone.app.testing',
    'collective.betterbrowser[pyquery]',
    'seantis.plonetools[tests]',
    'mock'
]

cover_require = [
    'seantis.cover.people'
]


def get_long_description():
    readme = open('README.rst').read()
    history = open(os.path.join('docs', 'HISTORY.rst')).read()
    contributors = open(os.path.join('docs', 'CONTRIBUTORS.rst')).read()

    # cut the part before the description to avoid repetition on pypi
    readme = readme[readme.index(description) + len(description):]

    return '\n'.join((readme, contributors, history))


setup(
    name=name, version=version, description=description,
    long_description=get_long_description(),
    classifiers=[
        'Framework :: Plone',
        'Framework :: Plone :: 4.3',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7'
    ],
    keywords='plone seantis people persons organizations positions',
    author='Seantis GmbH',
    author_email='info@seantis.ch',
    url='https://github.com/seantis/seantis.people',
    license='GPL v2',
    packages=find_packages(exclude=['ez_setup']),
    namespace_packages=['seantis'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'Plone>=4.3',
        'plone.api>=1.3.0',
        'five.grok',
        'plone.behavior',
        'plone.app.dexterity [grok, relations]',
        'plone.app.referenceablebehavior',
        'plone.app.registry',
        'plone.formwidget.datetime',
        'seantis.plonetools>=0.16',
        'collective.js.underscore',
        'collective.dexteritytextindexer',
        'tablib>=0.10.0',
        'isodate'
    ],
    extras_require=dict(
        tests=tests_require,
        cover=cover_require
    ),
    entry_points="""
    # -*- Entry points: -*-

    [z3c.autoinclude.plugin]
    target = plone
    """
)
