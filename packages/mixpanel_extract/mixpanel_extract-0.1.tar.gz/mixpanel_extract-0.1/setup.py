from setuptools import setup

setup(
    name='mixpanel_extract',
    version='0.1',
    description='Extract Mixpanel raw events and store on S3',
    license = "GPLv2",
    keywords = "mixpanel s3 etl",
    url='https://github.com/pior/mixpanel-extract',
    author='Pior Bastida    ',
    author_email='pior@pbastida.net',

    packages=['mixpanel_extract'],

    install_requires = ['boto'],

    entry_points={
        "console_scripts": [
            'mixpanel-extract = mixpanel_extract.commands:mixpanel_extract',
        ],
    },
)
