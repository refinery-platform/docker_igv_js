import requests
import subprocess
import sys
import time
import unittest

from test_utils import TestContainerRunner


class ContainerTest(unittest.TestCase):

    def get_url(self, name):
        command = "docker port {} | perl -pne 's/.*://'".format(name)
        port = subprocess.check_output(
            command,
            shell=True
        ).strip().decode('utf-8')
        url = 'http://localhost:{}'.format(port)
        for i in range(5):
            try:
                requests.get(url)
                return url
            except:
                print('Still waiting for server...')
                time.sleep(1)
        else:
            self.fail('Server never came up')

    def assert_expected_response(self, name, expected, path='/'):
        url = self.get_url(name)
        response = requests.get(url + path)
        # TODO: Not ideal for error pages
        self.assertEqual(200, response.status_code)
        self.assertIn(expected, response.text)

    # Good configurations:

    def test_good_home_page(self):
        self.assert_expected_response('good', '>IGV<')

    def test_input_data_url(self):
        self.assert_expected_response(
            'good',
            '{',
            path='/options.json'
        )

    # Bad configurations:

    def test_missing_assembly(self):
        self.assert_expected_response(
            'missing_assembly',
            'Unexpected 404 from https://s3.amazonaws.com/data.cloud.refinery-platform.org/data/igv-reference/hgFAKE/cytoBand.txt'
        )

    def test_multiple_assemblies(self):
        self.assert_expected_response(
            'multiple_assemblies',
            # If this happens often, could return more detail, but this is
            # enough, for now.
            'AssertionError()'
        )

    def test_no_parameters(self):
        self.assert_expected_response(
            'no_parameters',
            "KeyError('parameters',)"
        )


if __name__ == '__main__':
    with TestContainerRunner():
        suite = unittest.TestLoader().loadTestsFromTestCase(ContainerTest)
        result = unittest.TextTestRunner(verbosity=2).run(suite)

    if not result.wasSuccessful():
        sys.exit(1)
