from setuptools import setup, find_packages
import sys, os

here = os.path.abspath(os.path.dirname(__file__))
try:
    README = open(os.path.join(here, 'README.rst')).read()
except IOError:
    README = ''

version = "0.0.1"

setup(
    name='tgext.webassets',
    version=version,
    description="assets management extension for TurboGears2",
    long_description=README,
    classifiers=[],  # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
    keywords='turbogears2.extension',
    author='Alessandro Molina',
    author_email='alessandro.molina@axant.it',
    url='https://github.com/amol-/tgext.webassets',
    license='MIT',
    packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
    namespace_packages = ['tgext'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        "TurboGears2 >= 2.3.4",
        "webassets",
        "cssmin"
    ],
    entry_points="""
    # -*- Entry points: -*-
    """
)
