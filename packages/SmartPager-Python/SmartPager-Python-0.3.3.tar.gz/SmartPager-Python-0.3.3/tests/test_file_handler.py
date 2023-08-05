
import unittest
import os

from smartpager.utils import SPFileHandler


class TestRabbitClient(unittest.TestCase):

    secret = '1234567890123456789012345678901234567890'
    access_key = 'anshdlfkgnvjgituryeg'

    test_file_path = 'test.dat'
    second_file_path = 'second_test.dat'

    def setUp(self):
        self.file_handler = SPFileHandler(self.secret, self.access_key)

        if os.path.isfile(self.test_file_path) or os.path.isfile(self.second_file_path):
            raise AttributeError('Test file already exists - Recheck test file names.')

        open(self.test_file_path, 'a').close()
        open(self.second_file_path, 'a').close()

    def tearDown(self):
        os.remove(self.test_file_path)
        os.remove(self.second_file_path)

    def test_generate_url(self):

        with open(self.test_file_path, 'r') as f:
            signed_url = self.file_handler.generate_signed_url(f)

        self.assertIsNotNone(signed_url)

    def test_check_signed_url(self):

        with open(self.test_file_path, 'r') as f:
            signed_url = self.file_handler.generate_signed_url(f)
            signed_url_2 = self.file_handler.generate_signed_url(f)

        with open(self.second_file_path, 'r') as f:
            second_url = self.file_handler.generate_signed_url(f)

        self.assertEquals(signed_url, signed_url_2)
        self.assertNotEquals(signed_url, second_url)
