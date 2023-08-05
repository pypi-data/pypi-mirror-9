from setuptools import find_packages, setup

setup(
    name='kryptonium',
    version='0.1.3',
    url='https://github.com/danggrianto/kryptonium',
    license='GNU GPL v2.0',
    author='Daniel Anggrianto',
    author_email='daniel@anggrianto.com',
    description='Automation Framework using Selenium',
    long_description=__doc__,
    packages=find_packages(),
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    install_requires=[
        'selenium',
    ],
    test_suite='nose.collector',
    tests_require=['nose'],
)
