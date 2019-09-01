import unittest

from tests.FetcherTest import FetcherTest
from tests.KeyCreatorTest import KeyCreatorTest


def assemble_suite():
    # suite = unittest.load_tests(unittest.TestLoader(), unittest.TestSuite(), '.*Test.py')
    suite = unittest.TestSuite()
    suite.addTest(FetcherTest('test_that_we_skip_download_on_cache_hit'))
    return suite


if __name__ == '__main__':
    unittest.main()
    # runner = unittest.TextTestRunner()
    # runner.run(suite())

