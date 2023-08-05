from setuptools import setup

setup(
    name='group-by-attr',
    version='1.0.1',
    packages=('group_by_attr',),
    url='https://github.com/themattrix/python-group-by-attr',
    license='MIT',
    author='Matthew Tardiff',
    author_email='mattrix@gmail.com',
    install_requires=(),
    tests_require=(
        'coverage',
        'flake8',
        'nose',
        'pyflakes',),
    description=(
        'Group items in a sequence by the value of a shared attribute.'),
    classifiers=(
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy'))
