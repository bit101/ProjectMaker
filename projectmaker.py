import os
import re
import codecs
import shutil

import sublime
import sublime_plugin


__ST3 = int(sublime.version()) >= 3000
if __ST3:
    from STProjectMaker.configuration import ConfigurationReader
else:
    from configuration import ConfigurationReader


class ProjectMakerCommand(sublime_plugin.WindowCommand):
    def run(self):
        settings = sublime.load_settings("STProjectMaker.sublime-settings")
        templates_path_setting = settings.get('template_path')
        default_project_path_setting = settings.get('default_project_path')

        if not default_project_path_setting:
            if sublime.platform() == "windows":
                self.default_project_path = os.path.expanduser("~\\project_name").replace("\\", "/")
            else:
                self.default_project_path = os.path.expanduser("~/project_name")
        else:
            self.default_project_path = default_project_path_setting

        self.project_files_folder = settings.get('project_files_folder')
        self.non_parsed_ext = settings.get("non_parsed_ext")
        self.non_parsed_files = settings.get("non_parsed_files")
        self.existing_names = []
        self.plugin_path = os.path.join(sublime.packages_path(), "STProjectMaker")
        if not templates_path_setting:
            templates_path = os.path.expanduser("~/STProjectMakerTemplates")
            if os.path.exists(templates_path):
                self.templates_path = templates_path
            else:
                self.templates_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Sample-Templates")
        else:
            self.templates_path = os.path.abspath(templates_path_setting)
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
        if index > -1:
            self.chosen_template_name = self.template_names[index]
            self.chosen_template_path = os.path.join(self.templates_path, self.chosen_template_name)
            self.get_project_path()

    def get_project_path(self):
        self.window.show_input_panel("Project Location:",
                                     self.default_project_path,
                                     self.on_project_path,
                                     None, None)

    def on_project_path(self, path):
        self.project_path = path
        self.project_path_escaped = path.replace("/", "\\\\\\\\")
        self.project_name = os.path.basename(self.project_path)

        if os.path.exists(self.project_path):
            decision = sublime.ok_cancel_dialog(
                "Something already exists at " + self.project_path +
                ".\nDo you want to create project in that folder?" +
                "\n(Existing objects will not be overwritten)"
            )
            if decision:
                self.create_project()
        else:
            if not self.project_files_folder:
                self.create_project()
            else:
                self.get_project_name()

    def get_project_name(self):
        self.window.show_input_panel("Project Name:", self.project_name, self.on_project_name, None, None)

    def on_project_name(self, name):
        self.project_name = name
        self.create_project()

    def create_project(self):
        self.copy_project()
        self.get_tokens(self.project_path)
        self.get_token_values()

    def copy_project(self):
        if not os.path.exists(self.project_path):
            shutil.copytree(self.chosen_template_path, self.project_path)
        else:
            self.copy_in_non_empty()

    def copy_in_non_empty(self):
        self.existing_names = os.listdir(self.project_path)
        for name in os.listdir(self.chosen_template_path):
            srcname = os.path.join(self.chosen_template_path, name)
            dstname = os.path.join(self.project_path, name)
            if not os.path.exists(dstname):
                if os.path.isdir(srcname):
                    shutil.copytree(srcname, dstname)
                else:
                    shutil.copy2(srcname, dstname)

    def get_tokens(self, path):
        self.tokens = []
        self.tokenized_files = []
        self.tokenized_titles = []
        self.get_tokens_from_path(path)

    def get_tokens_from_path(self, path):
        files = os.listdir(path)
        for file_name in files:
            if file_name in self.non_parsed_files or file_name in self.existing_names:
                continue
            ext = os.path.splitext(file_name)[1]
            if ext in self.non_parsed_ext:
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

    def open_file(self, file_path, mode="r", return_content=True):
        has_exception = False
        try:
            file_ref = codecs.open(file_path, mode, "utf-8")
            content = file_ref.read()
            if return_content:
                file_ref.close()
                return content
            else:
                return file_ref
        except UnicodeDecodeError as e:
            has_exception = True

        try:
            file_ref = codecs.open(file_path, mode, "latin-1")
            content = file_ref.read()
            if return_content:
                file_ref.close()
                return content
            else:
                return file_ref
        except UnicodeDecodeError as e:
            has_exception = True

        sublime.error_message("Could not open " + file_path)

    def get_tokens_from_file(self, file_path):
        content = self.open_file(file_path)
        if content is None:
            return

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
            elif token == "project_path_escaped":
                self.token_values.append((token, self.project_path_escaped))
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
        self.token_values.append((self.tokens[self.token_index], token_value))
        self.token_index += 1
        self.get_next_token_value()

    def customize_project(self):
        self.replace_tokens()
        self.rename_files()
        self.find_project_file()
        self.read_configuration()
        self.window.run_command("open_dir", {"dir":self.project_path})

    def replace_tokens(self):
        for file_path in self.tokenized_files:
            self.replace_tokens_in_file(file_path)

    def replace_tokens_in_file(self, file_path):
        template = self.open_file(file_path)
        if template is None:
            return
            
        for token, value in self.token_values:
            r = re.compile(r"\${" + token + "}")
            template = r.sub(value, template)

        file_ref = self.open_file(file_path, "w+", False)
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
        if self.project_file is None:
            self.create_project_file()

    def create_project_file(self):
        file_name = self.project_name + ".sublime-project"

        if not self.project_files_folder:
            self.project_file = os.path.join(self.project_path, file_name)
        else:
            self.project_file = os.path.join(self.project_files_folder, file_name)

        file_ref = open(self.project_file, "w")
        file_ref.write(("{\n"
                        "    \"folders\":\n"
                        "    [\n"
                        "        {\n"
                        "            \"path\": \""+self.project_path+"\"\n"
                        "        }\n"
                        "    ]\n"
                        "}\n"));
        file_ref.close()

    def read_configuration(self):
        config_file = os.path.join(self.chosen_template_path, 'config.json')
        if os.path.exists(config_file):
            ConfigurationReader().read(config_file, self.project_path)

