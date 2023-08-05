from setuptools import setup


setup(
    name="pandoc-internal-references",
    version='0.4',
    description="Image attributes and internal referencing in markdown",
    packages=['internalreferences'],
    author="Aaron O'Leary",
    author_email='dev@aaren.me',
    license='BSD 2-Clause',
    url='https://github.com/aaren/pandoc-reference-filter',
    install_requires=['pandocfilters', 'pandoc-attributes'],
    entry_points={
        'console_scripts': [
            'internal-references = internalreferences:main',
        ],
    }
)
