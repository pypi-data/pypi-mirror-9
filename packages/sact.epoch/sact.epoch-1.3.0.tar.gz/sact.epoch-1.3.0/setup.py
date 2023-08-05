from setuptools import setup, find_packages

setup(
    name='sact.epoch',
    version="1.3.0",
    long_description=open("docs/source/overview.rst").read() + open("docs/source/changelog.rst").read(),
    description="Time object subclassing datetime allowing diverting local clock mecanism",
    # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Topic :: Software Development",
    ],
    keywords='sact time timedelta',
    author='SecurActive SA',
    author_email='opensource@securactive.net',
    url='http://github.com/securactive/sact.epoch',
    license='BSD License',
    package_dir={'': 'src'},
    packages=find_packages('src'),
    namespace_packages=['sact'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'setuptools',
        # -*- Extra requirements: -*-
        'python-dateutil',
        'zope.interface',
        'zope.component',
        'pytz',
    ],
    extras_require={'test': [
        'zope.testing',
        'zope.testrunner',
        # -*- Extra requirements: -*-
        'z3c.testsetup',
    ],
    },
    entry_points="""
    # -*- Entry points: -*-
    """,
)
