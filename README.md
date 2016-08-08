STProjectMaker
===================

A Sublime Text 2/3 plug-in to allow creating any kind of project from your own custom templates. 

Note, now works with BOTH ST2 and ST3! Thanks to [Daniel Shannon](https://github.com/phyllisstein) for that work.

## Installation

### Via Package Control:

1. Install Package Control from http://wbond.net/sublime_packages/package_control

2. From within Package Control, look for STProjectMaker and install.

### Manually:

Clone or download this project into a folder named "STProjectMaker" in your Sublime Text 2 or 3 Packages folder. If you're not sure where your Packages folder is, use menu `Preferences/Browse Packages...`

## Usage

From the Project Menu, choose "Create Project" or use the shortcut key Ctrl-Shift-N to invoke the project maker command.

Invoking the command will show a Quick Panel list of available templates.

Choose the template to base your project on.

You will be prompted to enter a path for your new project. Do so.

You will be prompted for values for any replaceable tokens in any template files or file names. Enter the values you want to use.

Newly created project folder will open in system file manager.

## Creating and Modifying Templates

A template is simply a folder that can contain any number and types of files and nested folders of files.

There are a few sample templates in the Sample-Templates directory. You can just copy those into your template dir to use them.

By default, templates are looked for in a folder named `STProjectMakerTemplates` in your home directory, you will have to create this folder and add your templates there. If no STProjectMakerTemplates exists, then `Sample-Templates` folder in plugin directory is used.

Alternately, you can  add a "template_path" property to your settings to tell STProjectMaker where to look for your templates. This is described below in the "Settings" section and would look like the following:
	{
		"template_path": "path/to/your/templates/"
	}

There is another repository, [https://github.com/bit101/STProjectMaker-templates](https://github.com/bit101/STProjectMaker-templates) that will be used to host additional templates created by other users.

### Tokens

Text files in the template may contain replaceable tokens in the form of `${token_name}`. When you create a new project, you will be prompted for values to use for each token found. The same token can be used multiple times in multiple files. You will only be prompted a single time for its value.

Example:

	Hello from ${user_name}

when supplied a value of `Keith` for the `user_name` token will become:

	Hello from Keith

### Tokenized File Names

Template file names may also be tokenized using the form `_token_name_.ext`. The leading underscore, token name and trailing underscore will be replaced by the value given.

Example:

	/foo/bar/baz/_info_file_.text

when supplied with a value of `data` for the `info_file` token will become:

	/foo/bar/baz/data.text

### Predefined Tokens

There are three predefined tokens:

`${project_path}` in text files will be replaced by the absolute path of the new project directory. This will always use forward slashes ("/") as path separators, even on Windows. Windows will generally use either forward or backslashes.

`${project_path_escaped}` is the same as `${project_path}` but on Windows only, a double backslash ("\\\\") will be used for path separation.

`${project_name}` in text files or `_project_name_` as a file name will be replaced by the base name of the project directory.

Example:

Project path is `/foo/bar/baz/MyProject/`

`project_path` will be replaced by `/foo/bar/baz/MyProject/`

`project_path_escaped` would be the same as `project_path` on OS X or Linux, but on Windows would be `c:\\foo\\bar\\baz\\MyProject\\`

`project_name` will be replaced by `MyProject`

### Settings

You can access STProjectMaker setting via the menu `Preferences / Package Settings / Project Maker` and then `Settings - Default` or `Settings - User`. Generally you should leave the default settings as-is and add your own settings to user settings.

The available settings are:

`non_parsed_ext` This is a list of file extensions that will not be parsed for token replacement. Files matching these extensions will still be copied to your project however.

`non_parsed_files` This is a list of individual file names that will not be parsed for token replacement. Currently this includes `build.xml` as Ant build files will generally have tokens in the same format as STProjectMaker tokens and STProjectMaker will try to replace these. Files matching these non-parsed file names will still be copied to the new project.

`template_path` As described above. This is the path where STProjectMaker will look for your templates. It is best to set this to something outside of the STProjectMaker directory so updates/upgrades/reinstalls will not delete or overwrite your templates. If not set, this defaults to `~/STProjectMakerTemplates`.

`project_files_folder` This is the path where STProjectMaker will save the autogenerated `.sublime-project` file. This defaults to the project path. Note that if your template includes its own `.sublime-project` file, it will simply be copied over as usual and this setting will have no effect.

`default_project_path` This is the path that is displayed by default when STProjectMaker asks for the Project Location. This defaults to `~/project_name`.

### Sublime Project files

If the chosen template has a `.sublime-project` file in the top level, that file will be copied over and processed like any other file in the template. However, if this does not exist, a default `.sublime-project` file will be created using the `project_name` token as its base name. 

### Ignored Files

Obviously, you don't want to try to do token replacement in binary files. The plug-in has a long list of file types that it will ignore when doing token replacement. You can always add your own if any files in your templates cause a problem. The list is contained in the `STProjectMaker.sublime-settings` file. Note, these files _will_ be copied into the project. They will just not be parsed for tokens.

### Auto File Downloading and Other Tasks

Todd Anderson (http://custardbelly.com/blog/) has created an additional configuration feature that I have added to the project. This allows additional functions to be run after the project is created to perform additional tasks. 

The one task it is currently capable of performing is downloading files and adding them to your project. This can be useful if you want every project you create to have the latest version of a particular library such as jQuery. The files to download are defined with a `config.json` file in the template. You can see an example of how this works in the `AppRequire.js` template. Known issue: the file task will fail on https urls under Linux. This is because the version of Python bundled with Sublime Text under Linux does not include the ssl module for reasons I am not quite clear on.

Note that if your template does not have a `config.json` file, this step will be ignored. Additional tasks can be created following the current example. Thus, it is sort of plug-in for a plug-in.
