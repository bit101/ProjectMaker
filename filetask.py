""" File task helper for configurations in STProjectMaker """

import os, errno
import sublime
__ST3 = int(sublime.version()) >= 3000
if __ST3:
    from urllib.error import URLError
    from urllib.request import urlopen
else:
    from urllib2 import URLError
    from urllib2 import urlopen

class DownloadError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class RemoteFileFetchTask:
    """ Reads in file objects in the following format and downloads them to disk: {'name':'str', 'url':'str', 'locations':['str']} """

    def read_file(self, url):
        try:
            response = urlopen(url)
            return response.read()
        except URLError as e:
            raise DownloadError(e.reason)
        
    def write_file(self, contents, to_file_path):
        with open(to_file_path, 'w') as f:
            f.write(contents)
            f.close()
            return os.path.exists(to_file_path)

    def execute(self, filelist, root_path):
        exceptions = []
        for file_obj in filelist:
            file_url = file_obj['url']
            file_ext = os.path.splitext(file_url)[1]
            file_name = file_obj['name']
            locations = file_obj['locations']

            try:
                contents = self.read_file(file_url)
            except DownloadError as e:
                exceptions.append('Could not load ' + file_url + '. [Reason]: ' + e.value)
                sublime.error_message("Unable to download:\n " + file_url + "\nReason:\n " + e.value + "\nNote: Sublime Text 2 on Linux cannot deal with https urls.")
                continue

            for location in locations:
                directory = os.path.join(root_path, location)
                # try to create directory listing if not present.
                try:
                    os.makedirs(directory)
                except OSError as e:
                    # if it is just reporting that it exists, fail silently.
                    if e.errno != errno.EEXIST:
                        raise e
                # write to location.
                filepath = os.path.join(directory, file_name + file_ext)
                self.write_file(contents, filepath)

        return exceptions
