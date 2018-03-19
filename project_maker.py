import codecs
import os
import re
import shutil
from collections import OrderedDict

import sublime
import sublime_plugin
import json

class ProjectMakerCommand(sublime_plugin.WindowCommand):

    def run(self):
        # declare some basic variables for later use
        self.existing_names = []
        self.templates = []
        # start step-wise execution of methods
        self.get_settings()

    def get_normalized_path(self, key):
        path = self.settings.get(key)
        path = sublime.expand_variables(path, {"packages": sublime.packages_path()})
        return os.path.normpath(os.path.expanduser(path))

    def get_settings(self):
        """Step 1 - Get settings."""
        self.settings = sublime.load_settings("ProjectMaker.sublime-settings")
        # get settings
        self.template_dir = self.get_normalized_path("template_dir")
        self.project_dir = self.get_normalized_path("project_dir")
        self.non_parsed_ext = self.settings.get("non_parsed_ext")
        self.non_parsed_files = self.settings.get("non_parsed_files")
        self.get_templates()

    def get_templates(self):
        """Step 2 - Get templates."""
        try:
            self.templates = next(os.walk(self.template_dir))[1]
        except FileNotFoundError as e:
            msg = "ProjectMaker: Project folder does not exist."
            self.window.status_message(msg)
            print(msg)
            print(template_dir)
        else:
            if self.templates:
                self.templates.sort()
                self.choose_template()
            else:
                print("No valid templates found.")

    def choose_template(self):
        """Step 3 - Choose a template from list."""
        self.window.show_quick_panel(self.templates, self.on_template_chosen)

    def on_template_chosen(self, index):
        """Step 4 - """
        if index > -1:
            self.chosen_template_path = os.path.join(
                self.template_dir, self.templates[index]
            )
            self.get_project_path()

    def get_project_path(self):
        """Step 5 - Get project path."""
        default = "MyProject"
        panel = self.window.show_input_panel(
            "Project Location:",
            os.path.join(self.project_dir, default),
            self.on_project_path,
            None,
            None,
        )
        # preselect default text
        size = panel.size()
        selection = panel.sel()
        selection.add(sublime.Region(size - len(default), size))

    def on_project_path(self, path):
        self.project_path = path
        self.project_path_escaped = path.replace("/", "\\\\\\\\")
        self.project_name = os.path.basename(self.project_path)
        if os.path.exists(self.project_path):
            confirmed = sublime.ok_cancel_dialog(
                "Something already exists at:\n{}\nDo you want to create project in that folder?\n(Existing objects will not be overwritten)".format(
                    self.project_path
                )
            )
            if not confirmed:
                return
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
        if file_name[0:1] == "_" and file_name[dot_index - 1:dot_index] == "_":
            file_path = os.path.join(path, file_name)
            self.tokenized_titles.append(file_path)
            token = file_name[1: dot_index - 1]
            if token not in self.tokens:
                self.tokens.append(token)

    def get_tokens_from_file(self, file_path):
        with open(file_path ,"r") as f:
            content = f.read()
            if content is None:
                return

            r = re.compile(r"\${[^}]*}")
            matches = r.findall(content)
            if len(matches) > 0:
                self.tokenized_files.append(file_path)
            for match in matches:
                token = match[2:-1]
                if token not in self.tokens:
                    self.tokens.append(token)

    def get_token_values(self):
        self.token_values = []
        self.token_index = 0
        self.get_next_token_value()

    def get_next_token_value(self):
        # TODO: base tokenization on: # expand_variables(value, variables)??
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
                self.window.show_input_panel(
                    "Value for token \"" + token + "\"",
                    "",
                    self.on_token_value,
                    None,
                    None,
                )
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
        self.exec_tasks()
        self.open_project_window()

    def replace_tokens(self):
        for file_path in self.tokenized_files:
            self.replace_tokens_in_file(file_path)

    def replace_tokens_in_file(self, file_path):
        with open(file_path, "w+") as f:
            template = f.read()
            if template is None:
                return

            for token, value in self.token_values:
                r = re.compile(r"\${" + token + "}")
                template = r.sub(value, template)
            with self.open_file(file_path, "w+", False) as f:
                f.write(template)

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
        folder_path = self.project_files_folder or self.project_path
        self.project_file = os.path.join(folder_path, file_name)
        proj_setting = {"folders": [{"path": self.project_path}]}
        with open(self.project_file, "w") as proj_f:
            proj_f.write(sublime.encode_value(proj_setting, pretty=True))

    def exec_tasks(self):
        config_file = os.path.join(self.chosen_template_path, "tasks.json")
        if os.path.isfile(config_file):
            with open(config_file, "r") as f:
                tasks = json.load(f)
                for t in tasks:
                    self.run_exec(t)

    def run_exec(self, args):
        exec_args = {
            "target": "exec",
            "shell": True,
            "working_dir": self.project_path
        }
        cmd_args = exec_args.copy()
        cmd_args.update(args)
        target = cmd_args.pop("target")
        # somehow can not use self.window here
        sublime.active_window().run_command(target, cmd_args)

    def open_project_window(self):
        from time import sleep
        sleep(1)
        subl_cmd = {
            "shell": False,
            "cmd": [sublime.executable_path(), "--project", self.project_file]
            # "target": "shell_cmd",
            # "cmd": "{} --project {}".format(sublime.executable_path(), self.project_file)

        }
        self.run_exec(subl_cmd)

