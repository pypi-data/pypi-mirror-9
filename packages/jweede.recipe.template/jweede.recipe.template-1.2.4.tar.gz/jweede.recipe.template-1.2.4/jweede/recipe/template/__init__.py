"""
Buildout recipe for making files out of Jinja2 templates.
"""

__author__ = 'Torgeir Lorange Ostby <torgeilo@gmail.com>'
__version__ = '1.2.4'

import logging
import os
import re
import sys

import jinja2
import zc.buildout
from zc.recipe.egg.egg import Eggs
from zope.dottedname.resolve import resolve as resolve_dotted


log = logging.getLogger(__name__)


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

        # Add buildout dir to python path so custom filter can be imported
        sys.path.append(self.buildout['buildout']['directory'])

        # Validate presence of required options
        if not ("template-file" in options or "input" in options):
            log.error("You need to specify a template-file or input")
            raise zc.buildout.UserError("No template file specified")
        if not ("target-file" in options or "output" in options):
            log.error("You need to specify a target-file or output")
            raise zc.buildout.UserError("No target file specified")

    def install(self):
        """
        Recipe install function.
        """

        # Helper functions

        def split(s):
            """
            Template filter splitting on any whitespace.
            """

            return re.split(r'\s+', s.strip())

        def as_bool(s):
            """
            Template filter which translates the given string into a boolean.
            """

            return s.lower() in ("yes", "true", "1", "on")

        def strip_dict(d):
            """
            Strips the values of a dictionary in place. All values are assumed
            to be strings. The same dictionary object is returned.
            """

            for k, v in d.iteritems():
                d[k] = v.strip()
            return d

        # Validate template and target lists
        template_file_option = self.options.get(
            "template-file",
            self.options.get("input"),
        )
        target_file_option = self.options.get(
            "target-file",
            self.options.get("output"),
        )
        template_files = split(template_file_option)
        target_files = split(target_file_option)
        if len(template_files) != len(target_files):
            raise zc.buildout.UserError(
                "The number of template and target files must match"
            )

        # Validate and normalise target executable option
        target_executables = split(self.options.get("target-executable",
                                                    "false"))
        target_executables = [as_bool(v) for v in target_executables]
        if len(target_executables) == 1:
            value = target_executables[0]
            target_executables = (value for i in xrange(len(template_files)))
        else:
            if len(target_executables) != len(template_files):
                raise zc.buildout.UserError(
                    "The number of target executables"
                    "must 0, 1 or match the number of template files"
                )

        # Assemble lists
        files = zip(template_files, target_files, target_executables)

        # Assemble template context
        context = strip_dict(dict(self.options))

        # Handle eggs specially
        if "eggs" in context:
            log.info("Making working set out of the eggs")
            eggs = Eggs(self.buildout, self.options["recipe"], self.options)
            names, eggs = eggs.working_set()
            context["eggs"] = eggs

        # Make recursive dict to be enable access dashed values.
        context['context'] = context

        # Make options from other parts available.
        part_options = SafeBuildout(self.buildout)
        if 'parts' not in context.keys():
            context.update({'parts': part_options})
        else:
            log.error(
                "You should not use parts as a name of a variable,"
                " since it is used internally by this recipe"
            )
            raise zc.buildout.UserError("parts used as a variable in %s"
                                        % self.name)

        filters = self.options.get('jinja2_filters')
        if filters:
            jinja2_filters = {}
            filters = filters.split()
            for filter_ in filters:
                try:
                    jinja2_filters[filter_.split('.')[-1]] = resolve_dotted(filter_)
                except ImportError, e:
                    raise zc.buildout.UserError("Filter '%s' not found.\n%s"
                                                % (filter_, e))
        else:
            jinja2_filters = {}

        filters = {
            "split": split,
            "as_bool": as_bool,
            "type": type,
            "eval": eval,
            "re_escape": re.escape,
        }
        filters.update(jinja2_filters)

        # Set up jinja2 environment
        jinja2_env = self._jinja2_env(filters=filters)

        # Load, render, and save files
        for template_file, target_file, executable in files:
            template = self._load_template(jinja2_env, template_file)
            output = template.render(**context)

            # Make target file
            target_file = os.path.abspath(target_file)
            self._ensure_dir(os.path.dirname(target_file))

            fp = open(target_file, "wt")
            fp.write(output)
            fp.close()

            # Chmod target file
            if executable:
                os.chmod(target_file, 0755)

            self.options.created(target_file)

        return self.options.created()

    update = install

    def _jinja2_env(self, filters=None):
        """
        Creates a Jinja2 environment.
        """

        base = os.path.abspath(os.path.join(
            self.buildout["buildout"]["directory"],
            self.options.get("base-dir", "")),
        )
        env = jinja2.Environment(loader=jinja2.FileSystemLoader(base))
        if filters:
            env.filters.update(filters)
        return env

    @staticmethod
    def _load_template(env, path):
        """
        Tried to load the Jinja2 template given by the environment and
        template path.
        """

        try:
            return env.get_template(path)
        except jinja2.TemplateNotFound, e:
            log.error("Could not find the template file: %s" % e.name)
            raise zc.buildout.UserError("Template file not found: %s" % e.name)

    @staticmethod
    def _ensure_dir(directory):
        """
        Ensures that the specified directory exists.
        """

        if directory and not os.path.exists(directory):
            os.makedirs(directory, 0755)


class SafeBuildout(object):

    def __init__(self, dict_like):
        self.dict_like = dict_like
        self.get = dict_like.get
        self.keys = dict_like.keys

    def __getattr__(self, item):
        return self.dict_like.get(item)
