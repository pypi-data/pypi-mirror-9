# jingerly
[![Build Status](https://travis-ci.org/WilliamMayor/jingerly.svg?branch=master)](https://travis-ci.org/WilliamMayor/jingerly)
[![Latest Docs](https://readthedocs.org/projects/jingerly/badge/?version=latest)](http://jingerly.readthedocs.org/en/latest/)
Project templating using Jinja2.

Easily create a blank project skeleton from a project template using the following features:

- Jinja2 templated files
- Templated file/folder names
- Download files from the Internet
- Copy local files into the project
- Run custom scripts before and after creation

## Usage

Create a new project directory from a project template:

    $ jingerly ~/templates/web ~/projects/next-big-thing

This copies over all of the files in `~/templates/web` and puts them in `~/projects/next-big-thing`.

### With Template Variables

Let's say your project template has a template `README.md` file that looks like this (using the Jinja2 templating language):

    # {{ project_name }}
    {{ short_desc }}

You can fill in those variables like this:

    $ jingerly ~/templates/web ~/projects/next-big-thing \
        --project_name=nbt \
        --short_desc="It's going to be awesome"

You'll see a file in `~/projects/next-big-thing/README.md` that looks like this:

    # nbt
    It's going to be awesome

jingerly automatically defines the variables `IN` and `OUT` for you to use in your templates. `IN` is the template directory you provide (`~/templates/web`) and `OUT` is the output directory (`~/projects/next-big-thing`).

### With Variable File/Folder Names

The file and folder names are run through Jinaj2 too. So you can have a directory template tree that looks like this:

    web/
        {{project_name}}/
            {{project_name}}.py
        README.md

Then you can run the previous `jingerly` command and see this:

    next-big-thing/
        nbt/
            nbt.py
        README.md

### With Interactivity

If you don't want to list your variable names and values on the command line you can fill them in interactively:

    $ jingerly ~/templates/web ~/projects/next-big-thing --interactive
    Value for project_name (leave blank to ignore): nbt
    Value for short_desc (leave blank to ignore): It's going to be awesome

### With Pre-Defined Variable Values

If you create a file called `jingerly.env` in your project template then jingerly will automatically pick up the values you define inside it. It's read in as a Python file so your variable definitions must be in the Pythyon syntax.

    web/
        {{project_name}}/
            {{project_name}}.py
        README.md
        jingerly.env

`jingerly.env`:

    project_name = 'nbt'
    short_desc = "It's going to be awesome"

### With Files Downloaded from the Internet

You might want to download a file when you create a new project, so jingerly adds a download filter into Jinja2. Let's say you want the latest version of jQuery so you create a template file called `jquery.js` in your project template:

    web/
        {{project_name}}/
            {{project_name}}.py
            static/
                jquery.js
        README.md
        jingerly.env

`jquery.js`:

    {{ "http://code.jquery.com/jquery-latest.min.js" | download }}

### With Files Copied Locally

You might want to copy a file in from somewhere else.

    gitignore
    web/
        .gitignore
        {{project_name}}/
            {{project_name}}.py
            static/
                jquery.js
        README.md
        jingerly.env

`.gitignore`:

    {{ OUT + "/../gitignore" | copy }}

### With Custom Scripts

jingerly also lets you define some scripts to be run when you create a new project. Create a file called `jingerly.pre` or `jingerly.post` in your project template and make it executable.

    gitignore
    web/
        .gitignore
        {{project_name}}/
            {{project_name}}.py
            static/
                jquery.js
        README.md
        jingerly.env
        jingerly.post

`jingerly.post`:

    #! /bin/bash

    virtualenv {{ OUT }}/venv
    . {{ OUT }}/venv/bin/activate
    pip install --upgrade pip
    pip install flask
    pip freeze > {{ OUT }}/requirements.txt

This will result in:

    next-big-thing/
        .gitignore
        nbt/
            nbt.py
            static/
                jquery.js
        README.md
        venv/
        requirements.txt

The scripts are run through Jinja2 before they're executed. `jingerly.pre` scripts will run after the template directory has been copied over into the output directory but before any templating has occurred. `jingerly.post` scripts will be run after Jinja2 has finished rendering the new project.

## Installation

The easiest way to install everything is to use pip:

    $ pip install jingerly

This installs the `jingerly` command line script as well as the Python module (should you want it).

If you don't want to install everything globally then you can use a virtualenv, I like to keep mine in `/usr/local`:

    $ cd /usr/local
    $ virtualenv jingerly
    $ . jingerly/bin/activate
    $ pip install jingerly
    $ ln -s ../jingerly/bin/jingerly bin/jingerly

Or, if you wanted to grab the source code:

    $ git clone https://github.com/WilliamMayor/jingerly.git
    $ cd jingerly
    $ virtualenv venv
    $ . venv/bin/activate
    $ pip install -r requirements.txt

From here you can run the tests using nose:

    $ nosetests

## Examples

There's an example in the examples directory that demonstrates the features mentioned in this README.
