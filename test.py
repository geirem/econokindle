import unittest

from tests.FetcherTest import FetcherTest


def assemble_suite():
    suite = unittest.TestSuite()
    suite.addTest(FetcherTest('test_that_we_skip_download_on_cache_hit'))
    return suite


if __name__ == '__main__':
    unittest.main()

