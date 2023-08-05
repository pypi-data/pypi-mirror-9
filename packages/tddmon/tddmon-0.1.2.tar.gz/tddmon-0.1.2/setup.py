from setuptools import setup, find_packages

with open('README.rst') as file:
    long_description = file.read()

setup(
    name="tddmon",
    version="0.1.2",
    description='TDD flow monitor.',
    long_description=long_description,
    url="http://kidosoft.pl",
    author="Jakub STOLARSKI (Dryobates)",
    author_email="jakub.stolarski@kidosoft.pl",
    license="beerware",
    keywords="tdd, testing",
    packages=find_packages('src', exclude=['example*']),
    package_dir={'': 'src'},
    entry_points={
        'console_scripts': [
            'tddmon=tddmon.__main__:main',
        ]
    },
    install_requires=[
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
