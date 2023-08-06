from setuptools import setup

setup(
    name = "pysteamkit",
    version = "0.0.1",
    author = "Ryan Kistner",
    author_email = "azuisleet@gmail.com",
    description = ("A library for working with Steam"),
    license = "",
    keywords = "steam pysteamkit",
    url = "https://bitbucket.org/AzuiSleet/pysteamkit",
    packages=['pysteamkit', 'pysteamkit.steam3', 'pysteamkit.protobuf'],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Internet",
    ],
)
