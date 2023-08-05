# -*- coding: utf-8 -*-
"""
Buildout recipe for making files out of Jinja2 templates.

Original author: Torgeir Lorange Ostby <torgeilo@gmail.com>

"""

from __future__ import division, print_function, unicode_literals

import os
import logging

import jinja2
import zc.buildout
from zc.recipe.egg.egg import Eggs

try:
    ## python2
    from pipes import quote
except ImportError:
    ## python3
    from shlex import quote


log = logging.getLogger(__name__)

ADD_BUILTINS = ['int', 'len', 'min', 'max', 'all', 'any', 'sorted', 'zip', 'bool', 'type']


## Jinja filters ##
def as_bool(s):
    """
    Template filter which translates the given string into a boolean.
    """

    if s.lower() in ("yes", "true", "1", "on"):
        return True
    elif s.lower() in ("no", "false", "0", "off"):
        return False
    raise ValueError("Cannot cast '{}' as bool".format(s))


## Helpers ##

def ensure_dir(directory):
    """
    Ensures that the specified directory exists.
    """

    if directory and not os.path.exists(directory):
        os.makedirs(directory)

def get_template(env, path):
    """
    Override env.get_template() to log the error message and send a zc.buildout exception instead.
    """

    try:
        return env.get_template(path)
    except jinja2.TemplateNotFound as e:
        log.error("Could not find the template file: %s", e.name)
        raise zc.buildout.UserError("Template file not found: {}".format(e.name))


## Recipe ##

class Recipe(object):
    """
    Buildout recipe for making files out of Jinja2 templates. All part options
    are directly available to the template. In addition, all options from all
    parts listed in the buildout section pluss the options from the buildout
    section itself are available to the templates through parts.<part>.<key>.

    If an eggs option is defined, the egg references are transformed into a
    pkg_resources.WorkingSet object before given to the template.
    """

    def __init__(self, buildout, name, options):
        self.buildout = buildout
        self.name = name
        self.options = options

        # Validate presence of required options
        if not "template-file" in options:
            log.error("You need to specify a template-file")
            raise zc.buildout.UserError("No 'template-file' specified")

        if not "target-file" in options:
            log.error("You need to specify a target-file")
            raise zc.buildout.UserError("No 'target-file' specified")

    def install(self):
        """
        Recipe install function.
        """

        parse_list = lambda s: s.strip().split()

        # Validate template and target lists
        template_files = parse_list(self.options["template-file"])
        target_files = parse_list(self.options["target-file"])
        if len(template_files) != len(target_files):
            raise zc.buildout.UserError(
                    "The number of template and target files must match")

        # Validate and normalise target executable option
        target_executables = parse_list(self.options.get("target-executable", "false"))
        target_executables = [as_bool(v) for v in target_executables]
        if len(target_executables) == 1:
            value = target_executables[0]
            target_executables = (value for i in range(len(template_files)))
        else:
            if len(target_executables) != len(template_files):
                raise zc.buildout.UserError("The number of target executables"
                        "must 0, 1 or match the number of template files")

        # Assemble lists
        files = zip(template_files, target_files, target_executables)

        # Assemble template context
        context = {k: v.strip() for k, v in self.options.items()}

        # Handle eggs specially
        if "eggs" in context:
            log.info("Making working set out of the eggs")
            eggs = Eggs(self.buildout, self.options["recipe"], self.options)
            names, eggs = eggs.working_set()
            context["eggs"] = eggs

        # Make options from other parts available.
        part_options = self.buildout
        if 'parts' not in context:
            context.update({'parts': part_options})
        else:
            log.error("You should not use parts as a name of a variable,"
                      " since it is used internally by this receipe")
            raise zc.buildout.UserError("parts used as a variable in {}".format(self.name))

        # Set up jinja2 environment
        jinja2_env = self.create_jinja2_env(
            filters={
                "as_bool": as_bool,
                "shell_quote": quote,
            })

        # Load, render, and save files
        for template_file, target_file, executable in files:
            template = get_template(jinja2_env, template_file)
            output = template.render(**context)

            # Make target file
            target_file = os.path.abspath(target_file)
            ensure_dir(os.path.dirname(target_file))

            fp = open(target_file, "wt")
            fp.write(output)
            fp.close()

            # Chmod target file
            if executable:
                os.chmod(target_file, 0o755)

            self.options.created(target_file)

        return self.options.created()

    def update(self):
        """
        Recipe update function. Does the same as install.
        """

        self.install()

    def create_jinja2_env(self, filters=None):
        """
        Creates a Jinja2 environment.
        """

        base = os.path.abspath(os.path.join(
                self.buildout["buildout"]["directory"],
                self.options.get("base-dir", "")))

        env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(base),
            trim_blocks=True,
            lstrip_blocks=True,
        )

        if filters:
            env.filters.update(filters)

        ## Add some python builtins as jinja globals
        env.globals.update({name: __builtins__[name] for name in ADD_BUILTINS})

        return env
