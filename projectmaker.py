import sublime, sublime_plugin, os, shutil, re
from configuration import ConfigurationReader

class ProjectMakerCommand(sublime_plugin.WindowCommand):
	def run(self):
		self.non_parsed = [".jpg", ".gif", ".png", ".bmp", ".swf", ".swc", ".fla", ".mp3", ".mp4", ".ogg", ".m4v", ".wav"]
		self.plugin_path = os.path.join(sublime.packages_path(), "SublimeProjectMaker")
		self.templates_path = os.path.join(self.plugin_path, "Templates")
		self.template_names = []
		self.choose_template()

	def choose_template(self):
		files = self.get_templates()
		for file_name in files:
			if os.path.isdir(os.path.join(self.templates_path, file_name)):
				self.template_names.append(file_name)
		self.window.show_quick_panel(self.template_names, self.on_template_chosen)

	def get_templates(self):
		files = os.listdir(self.templates_path)
		files = [(f.lower(), f) for f in files]
		return [f[1] for f in sorted(files)]

	def on_template_chosen(self, index):
		self.chosen_template_name = self.template_names[index]
		self.chosen_template_path = os.path.join(self.templates_path, self.chosen_template_name)
		self.get_project_path()

	def get_project_path(self):
		self.project_name = "My" + self.chosen_template_name + "Project"
		if sublime.platform() == "windows":
			default_project_path = os.path.expanduser("~\\My Documents\\" + self.project_name)
		else:
			default_project_path = os.path.expanduser("~/Documents/" + self.project_name)
		self.window.show_input_panel("Project Location:", default_project_path, self.on_project_path, None, None)

	def on_project_path(self, path):
		self.project_path = path
		self.project_name = os.path.basename(self.project_path)

		if os.path.exists(self.project_path):
			sublime.error_message("Something already exists at " + self.project_path)
		else:
			self.create_project()

	def create_project(self):
		self.copy_project()
		self.get_tokens(self.project_path);
		self.get_token_values()

	def copy_project(self):
		shutil.copytree(self.chosen_template_path, self.project_path)

	def get_tokens(self, path):
		self.tokens = []
		self.tokenized_files = []
		self.tokenized_titles = []
		self.get_tokens_from_path(path)

	def get_tokens_from_path(self, path):
		files = os.listdir(path)
		for file_name in files:
			ext = os.path.splitext(file_name)[1];
			if ext in self.non_parsed:
				print "skipping" + file_name
				continue
			file_path = os.path.join(path, file_name)
			self.get_token_from_file_name(path, file_name)
			if os.path.isdir(file_path):
				self.get_tokens_from_path(file_path)
			else:
				self.get_tokens_from_file(file_path)

	def get_token_from_file_name(self, path, file_name):
		dot_index = file_name.find(".")
		if file_name[0:1] == "_" and file_name[dot_index-1:dot_index] == "_":
			file_path = os.path.join(path, file_name)
			self.tokenized_titles.append(file_path)
			token = file_name[1:dot_index-1]
			if not token in self.tokens:
				self.tokens.append(token)

	def get_tokens_from_file(self, file_path):
		file_ref = open(file_path, "rU")
		content = file_ref.read()
		file_ref.close()

		r = re.compile(r"\${[^}]*}")
		matches = r.findall(content)
		if len(matches) > 0:
			self.tokenized_files.append(file_path)
		for match in matches:
			token = match[2:-1]
			if not token in self.tokens:
				self.tokens.append(token)

	def get_token_values(self):
		self.token_values = []
		self.token_index = 0
		self.get_next_token_value()

	def get_next_token_value(self):
		# are there any tokens left?
		if self.token_index < len(self.tokens):
			token = self.tokens[self.token_index]
			# built-in values (may need to extract these):
			if token == "project_path":
				self.token_values.append((token, self.project_path))
				self.token_index += 1
				self.get_next_token_value()
			elif token == "project_name":
				self.token_values.append((token, self.project_name))
				self.token_index += 1
				self.get_next_token_value()
			# custom token. get value from user:
			else:
				self.window.show_input_panel("Value for token \"" + token + "\"", "", self.on_token_value, None, None)
		else:
			# all done. do replacements
			self.customize_project()

	def on_token_value(self, token_value):
		self.token_values.append((self.tokens[self.token_index], token_value));
		self.token_index += 1
		self.get_next_token_value()

	def customize_project(self):
		self.replace_tokens()
		self.rename_files()
		self.find_project_file()
		self.read_configuration()
		self.window.run_command("open_dir", {"dir":self.project_path});

	def replace_tokens(self):
		for file_path in self.tokenized_files:
			self.replace_tokens_in_file(file_path)

	def replace_tokens_in_file(self, file_path):
		file_ref = open(file_path, "rU")
		template = file_ref.read()
		file_ref.close()

		for token, value in self.token_values:
			r = re.compile(r"\${" + token + "}")
			template = r.sub(value, template)

		file_ref = open(file_path, "w")
		file_ref.write(template)
		file_ref.close()

	def rename_files(self):
		for file_path in self.tokenized_titles:
			for token, value in self.token_values:
				# we do NOT want to use a full path for a single file name!
				if token != "project_path":
					r = re.compile(r"_" + token + "_")
					if r.search(file_path):
						os.rename(file_path, r.sub(value, file_path))
						break

	def find_project_file(self):
		files = os.listdir(self.project_path)
		r = re.compile(r".*\.sublime-project")
		self.project_file = None
		for file_name in files:
			if r.search(file_name):
				self.project_file = os.path.join(self.project_path, file_name)
		if self.project_file == None:
			self.create_project_file()

	def create_project_file(self):
		file_name = self.project_name + ".sublime-project"
		self.project_file = os.path.join(self.project_path, file_name)
		file_ref = open(self.project_file, "w")
		file_ref.write(("{\n"
						"    \"folders\":\n"
						"    [\n"
						"        {\n"
						"            \"path\": \".\"\n"
						"        }\n"
						"    ]\n"
						"}\n"));
		file_ref.close()

	def read_configuration(self):
		config_file = os.path.join(self.chosen_template_path, 'config.json')
		if os.path.exists(config_file):
			ConfigurationReader().read(config_file, self.project_path)
