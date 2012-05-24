""" Configuration helper for SublimeProjectMaker """

import json
from filetask import RemoteFileFetchTask 

class ConfigurationReader:
	""" Reads JSON file configuration and executes associated tasks. """

	def __init__(self):
		self.file_task = RemoteFileFetchTask()
		# Add tasks associated with key in JSON.
		self.tasks = dict({
			"files": self.file_task
		})

	def load_config(self, filepath):
		f = open(filepath)
		configuration = json.loads(f.read())
		f.close()
		return configuration

	def read(self, filepath, destination_path):
		configuration = self.load_config(filepath)
		# Iterate through task list and run associated task.
		for key, value in self.tasks.iteritems():
			if key.lower() == 'files':
				exceptions = self.file_task.execute(configuration['files'], destination_path)
				if exceptions is not None:
					build_filename = 'build.log'
					f = open(os.path.join(destination_path, '../', build_filename), "w")
					exception_iter = iter(exceptions)
					message = 'The following problems occured from FileTask:\n'
					try:
						message += str(exception_iter.next()) + '\n'
					except StopIteration, e:
						pass
					f.write(message)
					f.close

		return configuration