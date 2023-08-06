import re
import os
import sys
import argparse
from importlib import import_module
import unittest.loader
import unittest.runner
import unittest.signals


__all__ = ['run_tests']


def parse_args():
    parser = argparse.ArgumentParser(description='Run test package.')
    add_optional_args(parser)
    parser.add_argument('package',
                        help='Test package name')
    parser.add_argument('patterns', nargs='*',
                        help='Test case filter list')
    parser.set_defaults(**arg_defaults)
    return parser.parse_args()

def add_optional_args(parser):
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

arg_defaults = {'verbosity': 1}

def main():
    args = parse_args()

    pkg = import_module(args.package)
    run_tests([pkg], patterns=args.patterns, verbosity=args.verbosity,
              failfast=args.failfast, catchbreak=args.catchbreak, buffer=args.buffer)

def run_tests(pkgs, patterns=[], exit=True, verbosity=1, failfast=None, catchbreak=None,
              buffer=None, warnings=None):
    tests = unittest.TestSuite()
    for pkg in pkgs:
        tests.addTest(load_tests_from_package(pkg, patterns))

    if catchbreak:
        unittest.signals.installHandler()
    test_runner = unittest.runner.TextTestRunner(verbosity=verbosity, failfast=failfast,
                                        buffer=buffer, warnings=warnings)
    result = test_runner.run(tests)
    successful = result.wasSuccessful()
    if exit:
        sys.exit(0 if successful else 1)
    return successful

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

def load_tests_from_package(pkg, patterns):
    tests = PackageTestSuite(pkg)
    for submod in import_modules_from_package(pkg):
        for test in iter_tests(unittest.loader.defaultTestLoader.loadTestsFromModule(submod)):
            if match(test.id(), patterns):
                tests.addTest(test)
    return tests

def import_modules_from_package(pkg):
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

def iter_tests(tests):
    if isinstance(tests, unittest.TestSuite):
        for t in tests:
            yield from iter_tests(t)
    else:
        yield tests

def match(name, patterns):
    if not patterns: return True
    for pattern in patterns:
        p = '[^.]*'.join(re.escape(letter) for letter in pattern)
        if re.search(p, name):
            return True

if __name__ == '__main__':
    main()
