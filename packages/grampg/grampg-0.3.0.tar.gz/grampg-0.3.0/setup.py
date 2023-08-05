from setuptools import setup

setup(
    name="grampg",
    version="0.3.0",
    packages=['grampg', 'grampg.tests', 'grampg.demo'],

    description="Simple and flexible password generation library.",
    long_description=open('README.txt').read(),

    license="GNU Affero General Public License (LICENSE.txt)",

    test_suite='grampg.tests',

    # Metadata for upload to PyPI.
    author="Elvio Toccalino",
    author_email="me@etoccalino.com",
    keywords="grumpy admin password generator",
    url="https://bitbucket.org/etoccalino/grampg",
)
