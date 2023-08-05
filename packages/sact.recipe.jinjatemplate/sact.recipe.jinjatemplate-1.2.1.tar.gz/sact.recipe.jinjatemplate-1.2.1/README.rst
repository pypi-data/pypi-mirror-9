=========================
sact.recipe.jinjatemplate
=========================

sact.recipe.jinjatemplate is a Buildout recipe for generating files
using Jinja2 templates. It's a friendly fork of
amplecode.recipe.template (no more maintained).

Buildout Options
================

* template-file (required): One or more Jinja2 template file paths.
* target-file (required): One of more target file paths. The number of files must match the number of template files.
* base-dir: Base directory of the Jinja2 environment. Template file paths are relative to this directory. Default is the Buildout directory.
* target-executable: One or more boolean flags (yes|no|true|false|1|0) indicating the executability of the target files. If only one flag is given it is applied to all target files.
* eggs: Reserved for a list of eggs, conveniently converted into a pkg_resources.WorkingSet when specified.

Additional options are simply forwarded to the templates, and options from all the other parts are made available through ``parts.<part-name>.<option-name>`` and ``parts[<part-name>][<option-name>]``.

Lists of Values
===============

The `split` filter was removed in the 1.2. It is still possible for a
recipe option to contain one or more values, separated by whitespace::

  #!/bin/sh
  {% for cmd in cmds.split() %}
     echo "{{ cmd }}"
  {% endfor %}

Minimal Example
===============

foo.txt is created from foo.txt.jinja2 without any extra options::

  [buildout]
  parts = foo

  [foo]
  recipe = sact.recipe.jinjatemplate
  template-file = foo.txt.jinja2
  target-file = foo.txt

Larger Example
==============

foo.txt is created from myapp/foo.txt.jinja2, bar.sh is created from myapp/bar.sh.jinja2, the second will be executable, and both templates can utilize the additional options specified::

  [buildout]
  parts = foo

  [foo]
  recipe = sact.recipe.jinjatemplate
  base-dir = myapp
  template-file =
      foo.txt.jinja2
      bar.sh.jinja2
  target-file =
      foo.txt
      bar.sh
  target-executable =
      false
      true
  project_name = Another Example
  author = Me


Templating Shell Scripts
========================

If you use this recipe to template shell scripts, it is STRONGLY
recommanded to use the filter 'shell_quote' to avoid bad surprises::

  #!/bin/sh
  rm -rf -- {{ path|shell_quote }}
