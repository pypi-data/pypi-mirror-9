from setuptools import setup, find_packages

version = '1.7.7'

setup(
    name='pyjon.descriptors',
    version=version,
    description=(
        "Provides a system of descriptors to read files "
        "and return objects"
    ),
    long_description=open("README.rst").read(),
    classifiers=[
        "Programming Language :: Python",
        "Topic :: Text Processing",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
    ],
    keywords='',
    author='Florent Aide, Jerome Collette, Jonathan Schemoul',
    author_email=(
        'florent.aide@gmail.com, '
        'collette.jerome@gmail.com, '
        'jonathan.schemoul@gmail.com'
    ),
    url='https://bitbucket.org/xcg/pyjon.descriptors',
    license='MIT',
    packages=find_packages(exclude=['ez_setup']),
    namespace_packages=['pyjon'],
    include_package_data=True,
    zip_safe=False,
    test_suite='nose.collector',
    tests_require=[
        'nose',
        'coverage',
    ],
    install_requires=[
        'setuptools',
        'lxml',
        'six',
        # -*- Extra requirements: -*-
    ],
    entry_points="""
      # -*- Entry points: -*-
    """,
)
