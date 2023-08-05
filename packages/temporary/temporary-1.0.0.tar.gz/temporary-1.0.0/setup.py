from setuptools import setup

setup(
    name='temporary',
    version='1.0.0',
    packages=('temporary',),
    url='https://github.com/themattrix/python-temporary',
    license='MIT',
    author='Matthew Tardiff',
    author_email='mattrix@gmail.com',
    install_requires=(
        'contextlib2',),
    tests_require=(
        'coverage',
        'flake8',
        'mock',
        'nose',
        'pyflakes',
        'simian',),
    description=(
        'Context managers for managing temporary files and directories.'),
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
