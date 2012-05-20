SublimeProjectMaker
===================

A Sublime Text 2 plug-in to allow creating any kind of project from your own custom templates.

## Installation

Clone or download this project into a folder named "SublimeProjectMaker" in your Sublime Text 2 Packages folder.

Optionally, set up a key binding. I like to override Control-Shift-N in menu `Preferences/Key Bindings - User`

	[
		{ "keys": ["ctrl+shift+n"], "command": "project_maker" }
	]

## Usage

Invoking the command will show a Quick Panel list of available templates.

Choose the template to base your project on.

You will be prompted to enter a path for your new project. Do so.

You will be prompted for values for any replaceable tokens in any template files or file names. Enter the values you want to use.

Newly created project folder will open in system file manager.

## Creating and Modifying Templates

A template is simply a folder stored in `<sublime packages dir>/SublimeProjectMaker/Templates/`. It can contain any number and types of files and nested folders of files.

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

There are two predefined tokens:

`${project_path}` in text files will be replaced by the absolute path of the new project directory.

`${project_name}` in text files or `_project_name_` as a file name will be replaced by the base name of the project directory.

Example:

Project path is `/foo/bar/baz/MyProject/`

`project_path` will be replaced by `/foo/bar/baz/MyProject/`

`project_name` will be replaced by `MyProject`