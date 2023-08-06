from setuptools import setup

__author__ = 'Onset Technology'

setup(
    name='OnPage HUB API Client',
    version='0.1.0',
    author='Onset Technology',
    author_email='support@onsettechnology.com',
    packages=['onpage_hub_api_client'],
    scripts=[] ,
    url='http://www.onpage.com',
    license='LICENSE',
    description='Send Page to pager using OnPage HUB API',
    long_description=open('README').read(),
    install_requires=[
        "suds >= 0.4",
        ],
)
