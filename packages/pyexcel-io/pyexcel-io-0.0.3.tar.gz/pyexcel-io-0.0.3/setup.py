try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages
import sys

with open("README.rst", 'r') as readme:
    README_txt = readme.read()

dependencies = []

if sys.version_info[0] == 2 and sys.version_info[1] < 7:
    dependencies.append('ordereddict')

setup(
    name='pyexcel-io',
    author="C. W.",
    version='0.0.3',
    author_email="wangc_2011@hotmail.com",
    url="https://github.com/chfw/pyexcel-io",
    description='A generic file extension for pyexcel',
    install_requires=dependencies,
    packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
    include_package_data=True,
    long_description=README_txt,
    zip_safe=False,
    tests_require=['nose'],
    license='General Publice License version 3',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Topic :: Office/Business',
        'Topic :: Utilities',
        'Topic :: Software Development :: Libraries',
        'Programming Language :: Python',
        'License :: OSI Approved :: BSD License',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: Implementation :: PyPy'
    ]
)
