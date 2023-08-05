__author__ = 'AssadMahmood'
import unittest
import asposecloud
import os.path
import json

from asposecloud.storage import Folder
from asposecloud.cells import Converter


class TestAsposeCells(unittest.TestCase):

    def setUp(self):
        with open('setup.json') as json_file:
            data = json.load(json_file)

        asposecloud.AsposeApp.app_key = str(data['app_key'])
        asposecloud.AsposeApp.app_sid = str(data['app_sid'])
        asposecloud.AsposeApp.output_path = str(data['output_location'])
        asposecloud.Product.product_uri = str(data['product_uri'])

    def test_convert_storage_file(self):
        folder = Folder()
        response = folder.upload_file('./data/test_convert_cell.xlsx')
        self.assertEqual(True, response)

        converter = Converter('test_convert_cell.xlsx')
        converter.convert('tiff')
        self.assertTrue(os.path.exists('./output/test_convert_cell.tiff'))

if __name__ == '__main__':
    unittest.main()
