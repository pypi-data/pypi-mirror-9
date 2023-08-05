from setuptools import setup, find_packages

try:
    long_description = open("README.rst").read()
except IOError:
    long_description = ""

setup(
    name="yify-sub",
    version="0.1.0",
    description="Download yify subtitle using only one command.",
    license="MIT",
    author="David",
    packages=find_packages(),
    install_requires=[
        'html2text==2014.12.29',
        'requests==2.5.1',
    ],
    long_description=long_description,
    entry_points={
        'console_scripts': [
            'yify=yify:main'
        ]
    },
)
