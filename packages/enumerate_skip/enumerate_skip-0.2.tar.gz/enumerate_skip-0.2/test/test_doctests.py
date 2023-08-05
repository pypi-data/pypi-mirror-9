import doctest
import enumerate_skip.funcs as es


def load_tests(loader, tests, ignore):
    tests.addTests(doctest.DocTestSuite(es))
    return tests
