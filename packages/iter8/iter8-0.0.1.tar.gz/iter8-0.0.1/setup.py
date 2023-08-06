from setuptools import setup, find_packages
import json

package = json.load(open('package.json'))

setup(
    name=str(package['name']),
    version=str(package['version']),
    url=str(package['homepage']),
    description=str(package['description']),
    long_description=open('README.rst').read(),
    author=str(package['author']['name']),
    author_email=str(package['author']['email']),
    license=open('LICENSE').read(),
    packages=find_packages(),
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Topic :: Text Processing :: General',
    ]
)
