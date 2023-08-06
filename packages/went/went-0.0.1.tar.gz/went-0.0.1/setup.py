from setuptools import setup
from pip.req import parse_requirements
from pip.exceptions import InstallationError

try:
    requirements = parse_requirements("requirements.txt")
    install_requires = [str(r.req) for r in requirements]
except InstallationError:
    install_requires = []

try:
    long_description = open("README.rst").read()
except IOError:
    long_description = ""

setup(
    name="went",
    version="0.0.1",
    description="Tools for implementing a webmention enpoint.",
    license="MIT",
    author="Giovanni T. Parra",
    author_email='fiatjaf@gmail.com',
    install_requires=install_requires,
    long_description=long_description,
    packages=['went']
)
