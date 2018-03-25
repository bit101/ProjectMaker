import codecs
import glob
import json
import os
import re
import shutil
from collections import OrderedDict

import sublime
import sublime_plugin
from .voodoo.main import render_skeleton

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
        data = {}
        envops = {
            # 'autoescape': True,
            'block_start_string': '[%',
            'block_end_string': '%]',
            'variable_start_string': '[[',
            'variable_end_string': ']]',
            # 'keep_trailing_newline': True,
        }
        render_skeleton(
            self.chosen_template_path,
            self.project_path,
            data=data,
            force=True,
            envops=envops,
        )
        self.ensure_project_file()
        self.exec_tasks()

    def ensure_project_file(self):
        files = glob.glob(os.path.join(self.project_path, "*.sublime-project"))
        if files:
            self.project_file = files[0]
        else:
            file_name = self.project_name + ".sublime-project"
            folder_path = self.project_files_folder or self.project_path
            self.project_file = os.path.join(folder_path, file_name)
            # TODO: check whether project path must be absolute
            proj_setting = {"folders": [{"path": self.project_path}]}
            with open(self.project_file, "w") as proj_f:
                proj_f.write(sublime.encode_value(proj_setting, pretty=True))

    def run_exec(self, args):  # TODO: should this be **kwargs?
        cmd_args = {"target": "exec", "shell": True, "working_dir": self.project_path}
        cmd_args.update(args)
        target = cmd_args.pop("target")
        # somehow can not use self.window here
        sublime.active_window().run_command(target, cmd_args)

    def exec_tasks(self):
        task_file = os.path.join(self.chosen_template_path, "tasks.json")
        if os.path.isfile(task_file):
            with open(task_file, "r") as f:
                tasks = json.load(f)
                for t in tasks:
                    self.run_exec(t)

    def open_project_window(self):
        subl_cmd = {
            "shell": False,
            "cmd": [sublime.executable_path(), "--project", self.project_file],
        }
        self.run_exec(subl_cmd)
