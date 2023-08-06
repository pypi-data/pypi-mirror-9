from setuptools import setup, find_packages

import testpkg

setup(
    name='python-testpkg',
    version='0.2',
    description='Run test package.',
    url='https://github.com/weijar/python-testpkg',
    author='weijarz',
    author_email='weijarz@gmail.com',
    license='MIT',

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Testing',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
    ],
    keywords='unittest test testrunner',

    py_modules=['testpkg'],

    entry_points={
        'console_scripts': [
            'testpkg=testpkg:main',
        ],
    },
)
