""" Unit tests for fileutil.py from SublimeProjectMaker project. """

import sys, os, unittest
# http://stackoverflow.com/questions/67631/how-to-import-a-module-given-the-full-path
import imp
fileutil = imp.load_source('fileutil', '../fileutil.py')

class TestConfigLoad(unittest.TestCase):
	"""Testing load and parse of config.json"""
	
	configuration = None
	
	def setUp(self):
		""" Python <2.7 psuedo setUpBeforeClass """
		if self.__class__.configuration is None:
			self.__class__.configuration = fileutil.load_config('config_test.json')

	def tearDown(self):
		self.__class__.configuration = None

	def test_load_config_not_none(self):
		self.assertTrue(self.__class__.configuration is not None)

	def test_config_has_file_array(self):
		self.assertTrue(type(self.__class__.configuration['files']) == list)

	def test_file_array_length(self):
		files = self.__class__.configuration['files']
		self.assertEqual(len(files), 2 )

	def test_file_read(self):
		files = self.__class__.configuration['files']
		url = files[0]['url']
		self.assertTrue(url is not None)
		self.assertTrue(fileutil.read_file(url) is not None)

	def test_file_write(self):
		files = self.__class__.configuration['files']
		url = files[0]['url']
		contents = fileutil.read_file(url)
		filepath = os.path.join(os.path.expanduser('~/Documents'), files[0]['name'])
		self.assertTrue(fileutil.write_file(contents, filepath))
		if os.path.exists(filepath):
			try:
				os.remove(filepath)
			except Exception, e:
				raise e

#if __name__ == '__main__':
#	unittest.main()

suite = unittest.TestLoader().loadTestsFromTestCase(TestConfigLoad)
unittest.TextTestRunner(verbosity=2).run(suite)