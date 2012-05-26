""" Unit tests for configuration.py and filetask.py from STProjectMaker project. """
""" [NOTE] filetask module imports sublime for error handling within the Sublime Text 2 IDE. Comment references to sublime to run tests properly. """

import sys, os, json, shutil, unittest
sys.path.append('../')
from configuration import ConfigurationReader
from filetask import RemoteFileFetchTask

class TestConfigurationLoad(unittest.TestCase):
	"""Testing load and parse of config.json"""
	
	configuration = None
	
	def setUp(self):
		""" Python <2.7 psuedo setUpBeforeClass """
		if self.__class__.configuration is None:
			config = ConfigurationReader()
			self.__class__.configuration = config.load_config('config_test.json')

	def test_load_config_not_none(self):
		self.assertTrue(self.__class__.configuration is not None)

	def test_config_has_file_array(self):
		self.assertTrue(type(self.__class__.configuration['files']) == list)

	def test_file_array_length(self):
		files = self.__class__.configuration['files']
		self.assertEqual(len(files), 2 )

	def test_file_read(self):
		files = self.__class__.configuration['files']
		file_obj = files[0]
		name = file_obj['name']
		url = file_obj['url']
		locations = file_obj['locations']
		self.assertTrue(url is not None)
		self.assertTrue(name is not None)
		self.assertEqual(len(locations), 1)

class TestFileTask(unittest.TestCase):
	"""Testing FileTask on configuration"""

	configuration = None
	task = None

	def setUp(self):
		""" Python <2.7 psuedo setUpBeforeClass """
		if self.__class__.configuration is None:
			f = open('config_test.json')
			self.__class__.configuration = json.loads(f.read())
			f.close()
		if self.__class__.task is None:
			self.__class__.task = RemoteFileFetchTask()

	def test_file_read(self):
		files = self.__class__.configuration['files']
		url = files[0]['url']
		contents = self.__class__.task.read_file(url)
		self.assertTrue(contents is not None)

	def test_file_write(self):
		files = self.__class__.configuration['files']
		url = files[0]['url']
		contents = self.__class__.task.read_file(url)
		filepath = os.path.join(os.curdir,files[0]['name'])
		self.assertTrue(self.__class__.task.write_file(contents, filepath))
		if os.path.exists(filepath):
			try:
				os.remove(filepath)
			except Exception, e:
				raise e

	def test_execute_from_list(self):
		files = self.__class__.configuration['files']
		self.__class__.task.execute(files, os.curdir)
		to_dir = os.path.join(os.curdir,'libs')
		self.assertTrue(os.path.exists(to_dir))
		if os.path.exists(to_dir):
			try:
				shutil.rmtree(to_dir)
			except Exception, e:
				raise e

	def test_exceptions_from_execute(self):
		files = [{'url':'httpf://code.jquery.com/jquery-latest.js', 'name':'badurltest', 'locations':[]}]
		exceptions = self.__class__.task.execute(files, os.curdir)
		self.assertEqual(len(exceptions), 1)

suite = unittest.TestSuite()
suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestConfigurationLoad))
suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestFileTask))
unittest.TextTestRunner(verbosity=2).run(suite)