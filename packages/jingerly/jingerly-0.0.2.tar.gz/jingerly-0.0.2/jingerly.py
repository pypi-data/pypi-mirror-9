import imp
import subprocess
import os
import shutil

import requests
from jinja2 import Environment, DebugUndefined, meta

ALLOWED_TYPES = [
    type(True), type(0), type(0.0), type(0l), type(0+0j), type(''), type(u''),
    type([]), type((1,)), type(set()), type({})]


def __walk(root, ignore):
    """Replicates :func:`os.walk` but filters out any files or folders
    whose name is found in *ignore*.
    """
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = filter(lambda dn: dn not in ignore, dirnames)
        filenames = filter(lambda fn: fn not in ignore, filenames)
        yield dirpath, dirnames, filenames


def __filter_copy(path):
    """Jinja2 filter that reads the contents of the file at *path* and returns it.
    """
    with open(path, 'rb') as fd:
        return fd.read()


def __filter_download(url):
    """Jinja2 filter that downloads the file at *url* and returns its contents.
    """
    return requests.get(url).content


def __make_env():
    """Creates a :class:`jinja2.Environment` and prepares it to be used by
    jingerly. We use a :class:`jinja2.DebugUndefined` undefined object so that
    when template variables are not provided they are left alone. This means we
     can use jingerly to template projects that use Jinja2
    """
    env = Environment(undefined=DebugUndefined)
    env.filters['copy'] = __filter_copy
    env.filters['download'] = __filter_download
    return env


def __make_variables(template_dir, output_dir, kwargs):
    """Returns a dictionary of the variables that will be passed into the template.
    Combines *template_dir* and *output_dir* with *kwargs* as 'IN' and 'OUT'
    repectively. Then processes *output_dir/jingerly.env* (if it exists).
    """
    variables = kwargs.copy()
    variables['IN'] = template_dir
    variables['OUT'] = output_dir
    env_path = os.path.join(template_dir, 'jingerly.env')
    if os.path.isfile(env_path):
        env = imp.load_source('module.name', env_path)
        for name in dir(env):
            if name.startswith('__'):
                continue
            attr = getattr(env, name)
            if type(attr) in ALLOWED_TYPES:
                variables[name] = attr
    return variables


def __make_renderer(env, variables):
    """Returns a function that takes some text and creates and renders a
    template from it using *env* and *variables*
    """
    def renderer(text):
        template = env.from_string(text)
        return template.render(**variables)
    return renderer


def __process_files(root, files, renderer):
    """Pass the contents of each file in *files* to *renderer*, changes the
    file name if needed.
    """
    for f in files:
        file_path = os.path.join(root, f)
        file_name = renderer(f)
        with open(file_path, 'rb') as fd:
            file_contents = renderer(fd.read())
        if file_name != f:
            os.remove(file_path)
            file_path = os.path.join(root, file_name)
        with open(file_path, 'wb') as fd:
            fd.write(file_contents)


def __process_dirs(root, dirs, renderer):
    """Changes any directory name in *dirs* that needs changing (rendering).
    """
    dir_names = []
    for d in dirs:
        dir_path = os.path.join(root, d)
        dir_name = renderer(d)
        dir_names.append(dir_name)
        if dir_name != d:
            shutil.move(dir_path, os.path.join(root, dir_name))
    return dir_names


def __run_script(script_path, renderer):
    """Renders the script at *script_path* then calls it"""
    if os.path.isfile(script_path):
        with open(script_path, 'rb') as fd:
            file_contents = renderer(fd.read())
        with open(script_path, 'wb') as fd:
            fd.write(file_contents)
        subprocess.call(script_path)


def __run_pre(output_dir, renderer):
    """Runs the `jingerly.pre` script"""
    script_path = os.path.join(output_dir, 'jingerly.pre')
    __run_script(script_path, renderer)


def __run_post(output_dir, renderer):
    """Runs the `jingerly.post` script"""
    script_path = os.path.join(output_dir, 'jingerly.post')
    __run_script(script_path, renderer)


def __clean(path):
    """Deletes the `jingerly` specific files, if they exist.
    """
    for name in ['jingerly.pre', 'jingerly.post', 'jingerly.env']:
        try:
            os.remove(os.path.join(path, name))
        except OSError:
            pass


def render(template_dir, output_dir, _ignore=None, **kwargs):
    """:func:`jingerly.__walk` through every file and directory in
    *template_dir*, render it using variable values in *kwargs*, and save the
    output in *output_dir*. The order things happen in is:

    1. Copy entire template to output directory
    2. Read variables from `jingerly.env`
    3. Run `jingerly.pre`
    4. Walk through output_dir processings files and directories
    5. Run `jingerly.post`
    6. Clean up any jingerly specific files
    """
    template_dir = os.path.abspath(template_dir)
    output_dir = os.path.abspath(output_dir)
    shutil.copytree(template_dir, output_dir)
    if _ignore is None:
        _ignore = ['.DS_Store', '.git']
    env = __make_env()
    variables = __make_variables(template_dir, output_dir, kwargs)
    renderer = __make_renderer(env, variables)
    __run_pre(output_dir, renderer)
    for root, dirs, files in __walk(output_dir, _ignore):
        __process_files(
            root, files, renderer)
        dirs[:] = __process_dirs(
            root, dirs, renderer)
    __run_post(output_dir, renderer)
    __clean(output_dir)


def find_variables(template_dir, _ignore=None):
    """:func:`jingerly.__walk` through every file and directory in
    *template_dir* returning a list of all of the variables. This is used
    for the interactive feature of the CLI.
    """
    template_dir = os.path.abspath(template_dir)
    if _ignore is None:
        _ignore = ['.DS_Store', '.git', 'jingerly.env']
    env = __make_env()
    known = __make_variables(template_dir, template_dir, {})
    unknown = set()
    for root, dirs, files in __walk(template_dir, _ignore):
        for f in files:
            ast = env.parse(f)
            unknown |= meta.find_undeclared_variables(ast)
            with open(os.path.join(root, f), 'rb') as fd:
                ast = env.parse(fd.read())
                unknown |= meta.find_undeclared_variables(ast)
        for d in dirs:
            ast = env.parse(d)
            unknown |= meta.find_undeclared_variables(ast)
    return filter(lambda n: n not in known, unknown)
