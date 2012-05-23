""" File task helper for configurations in SublimeProjectMaker """

import urllib2, os, errno

class RemoteFileFetchTask:
	""" Reads in file objects in the following format and downloads them to disk: {'name':'str', 'url':'str', 'locations':['str']} """

	def read_file(self, url):
		response = urllib2.urlopen(url)
		return response.read()

	def write_file(self, contents, to_file_path):
		with open(to_file_path, 'w') as f:
			f.write(contents)
			f.close()
			return os.path.exists(to_file_path)

	def execute(self, filelist, root_path):
		for file_obj in filelist:
			file_url = file_obj['url']
			file_ext = file_url.split('.').pop()
			file_name = file_obj['name']
			locations = file_obj['locations']
			contents = self.read_file(file_url)
			for location in locations:
				directory = os.path.join(root_path, location)
				# try to create directory listing if not present.
				try:
					os.makedirs(directory)
				except OSError, e:
					# if it is just reporting that it exists, fail silently.
					if e.errno != errno.EEXIST:
						raise e
				# write to location.
				filepath = os.path.join(directory, file_name + '.' + file_ext)
				self.write_file(contents, filepath)