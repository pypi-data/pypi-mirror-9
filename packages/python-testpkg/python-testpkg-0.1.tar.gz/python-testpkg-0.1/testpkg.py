import re
import os
import sys
import argparse
import unittest
from importlib import import_module
from unittest import loader, runner
from unittest.signals import installHandler


__all__ = ['run_tests']


def load_package_tests(pkg):
    """Load tests from a package's submodules."""
    
    tests = unittest.TestSuite()
    for submod in import_modules_in_package(pkg):
        tests.addTest(loader.defaultTestLoader.loadTestsFromModule(submod))
    return tests

class PackageTestSuite(unittest.TestSuite):

    def __init__(self, pkg):
        super().__init__()
        self._pkg = pkg

    def run(self, result):
        if hasattr(self._pkg, 'setUpPackage'):
            self._pkg.setUpPackage()
        super().run(result)
        if hasattr(self._pkg, 'tearDownPackage'):
            self._pkg.tearDownPackage()

def import_modules_in_package(pkg):
    """Import all modules under specific package."""

    if not is_package(pkg):
        raise TypeError('%s is not a package' % pkg.__name__)

    mods = []
    for fname in os.listdir(os.path.dirname(pkg.__file__)):
        if fname.endswith('.py') and not fname.startswith('__'):
            modname = os.path.splitext(os.path.basename(fname))[0]
            mods.append(import_module(pkg.__name__ + '.' + modname))
    return mods

def is_package(mod):
    return mod.__name__ == mod.__package__

def parse_args():
    parser = argparse.ArgumentParser(description='Run test package.')
    parser.add_argument('-v', '--verbose', dest='verbosity',
                        action='store_const', const=2,
                        help='Verbose output')
    parser.add_argument('-q', '--quiet', dest='verbosity',
                        action='store_const', const=0,
                        help='Quiet output')
    parser.add_argument('-f', '--failfast', dest='failfast',
                        action='store_true',
                        help='Stop on first fail or error')
    parser.add_argument('-c', '--catch', dest='catchbreak',
                        action='store_true',
                        help='Catch ctrl-C and display results so far')
    parser.add_argument('-b', '--buffer', dest='buffer',
                        action='store_true',
                        help='Buffer stdout and stderr during tests')
    parser.add_argument('pkgname', nargs=1,
                        help='Test package name')
    parser.add_argument('patterns', nargs='*',
                        help='Filters')
    return parser.parse_args()

def main():
    args = parse_args()
    run_tests(args.pkgname[0], patterns=args.patterns, verbosity=args.verbosity or 1,
              failfast=args.failfast, catchbreak=args.catchbreak, buffer=args.buffer)

def run_tests(pkgname, patterns=[], exit=True, verbosity=1, failfast=None, catchbreak=None,
              buffer=None, warnings=None):
    pkg = import_module(pkgname)
    tests = PackageTestSuite(pkg)
    num_tests = filter_tests(tests, load_package_tests(pkg), patterns)
    if not num_tests:
        print('No matched tests.', file=sys.stderr)
        if exit:
            sys.exit(1)

    if catchbreak:
        installHandler()
    test_runner = runner.TextTestRunner(verbosity=verbosity, failfast=failfast,
                                        buffer=buffer, warnings=warnings)
    result = test_runner.run(tests)
    if exit:
        sys.exit(not result.wasSuccessful())

def filter_tests(tests, all_tests, patterns):
    count = 0
    for test in iter_tests(all_tests):
        if match(test.id(), patterns):
            tests.addTest(test)
            count += 1
    return count

def iter_tests(tests):
    if hasattr(tests, '__iter__'):
        for t in tests:
            yield from iter_tests(t)
    else:
        yield tests

def match(name, patterns):
    if not patterns: return True
    for pattern in patterns:
        p = '.*'.join(re.escape(letter) for letter in pattern)
        if re.search(p, name, re.I):
            return True

if __name__ == '__main__':
    main()
