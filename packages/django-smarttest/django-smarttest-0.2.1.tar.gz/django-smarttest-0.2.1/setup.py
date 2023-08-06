from setuptools import setup, find_packages

with open('README.rst') as file:
    long_description = file.read()

setup(
    name="django-smarttest",
    version="0.2.1",
    description='Code snippets which help writing automated tests for Django.',
    long_description=long_description,
    url="http://kidosoft.pl",
    author="Jakub STOLARSKI (Dryobates)",
    author_email="jakub.stolarski@kidosoft.pl",
    license="beerware",
    keywords="django testing",
    packages=find_packages('src', exclude=['example*']),
    package_dir={'': 'src'},
    install_requires=[
        'mock',
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Framework :: Django',
        'Programming Language :: Python',
        'Topic :: Utilities'
    ],
)
