from distutils.core import setup

setup(
    # Application name:
    name="glowfi.sh",

    # Version number (initial):
    version="0.2.15",

    # Application author details:
    author="glowfi.sh Team",
    author_email="team@glowfi.sh",

    # Packages
    packages=["glowfish"],

    # Include additional files into the package
    include_package_data=True,

    # Details
    url="https://pypi.python.org/pypi/glowfi.sh",

    #
    # license="LICENSE.txt",
    description="Machine learning without the PhD. Now with machine guns and rocket launchers.",

    # long_description=open("README.txt").read(),

    # Dependent packages (distributions)
    install_requires=[
        "requests",
    ],
)
