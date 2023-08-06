from setuptools import setup, find_packages

# Hack to prevent stupid "TypeError: 'NoneType' object is not callable" error
# in multiprocessing/util.py _exit_function when running `python
# setup.py test` (see
# http://www.eby-sarna.com/pipermail/peak/2010-May/003357.html)
try:
    import multiprocessing
except ImportError:
    pass

setup(
    name='mock-django',
    version='0.6.8',
    description='',
    license='Apache License 2.0',
    author='David Cramer',
    author_email='dcramer@gmail.com',
    url='http://github.com/dcramer/mock-django',
    packages=find_packages(exclude=['tests', 'tests.*']),
    install_requires=[
        'Django>=1.4',
        'mock',
    ],
    tests_require=[
        'unittest2',
        'nose',
    ],
    test_suite='runtests.collector',
    zip_safe=False,
    include_package_data=True,
)
