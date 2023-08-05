from setuptools import setup, find_packages

setup(
    name="gyuto",
    version="0.1.2",
    author="John Askew",
    author_email="john.askew@gmail.com",
    packages=find_packages(),
    url="http://bitbucket.org/skew/gyuto",
    license="GNU General Public License v3 (GPLv3)",
    description="A tool to slice and dice vulnerability scan data",
    long_description=open("README").read(),
    install_requires=[
        "docopt==0.6.2",
        "lxml==3.3.5",
        "requests==2.3.0",
        "jinja2==2.7.3",
        "netaddr==0.7.10",
        "prettytable==0.7.2",
        ],
    entry_points={
        "console_scripts": [
            "gyuto = gyuto.cli:main",
            ],
        }
    )
