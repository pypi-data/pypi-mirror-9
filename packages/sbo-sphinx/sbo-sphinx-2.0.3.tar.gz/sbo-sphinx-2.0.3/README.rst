sbo-sphinx README
=================

Overview
--------

Safari Books Online technical documentation is now being written and collected
in a form that can be processed by `Sphinx <http://sphinx-doc.org/>`_, a utility
for generating documentation in HTML, PDF, Epub, and other formats from text
files using reST (reStructuredText) wiki markup.  In addition to writing docs
directly, we can have Sphinx grab API documentation from our core
programming languages:

* Python docstrings are collected using the sphinx-apidoc command.
* JSDoc-formatted comments in JavaScript are collected using the
  JsDoc Toolkit RST-Template library, which in turn uses jsdoc-toolkit.

Web service APIs can be documented using httpdomain from sphinx-contrib.

Installation
------------
``pip install sbo-sphinx``

To build JavaScript API documentation, you'll also need java and ant.

Settings
--------
sbo-sphinx uses the standard Sphinx `conf.py file <http://sphinx-doc.org/config.html>`_,
but offloads the vast majority of the configuration to an
``sbo_sphinx.conf`` module which should be appropriate for most SBO
projects.  Hence a minimal ``docs/conf.py`` file can be as simple as::

    from sbo_sphinx.conf import *

    project = 'my_project_name'

There should also be a ``docs/index.rst`` file to serve as the documentation
home page; see the one in this project for an example.

There are additional settings for the extensions which auto-generate Python
and JavaScript API documentation. See ``sbo_sphinx.apidoc`` and
``sbo_sphinx.jsdoc`` for details.

Usage
-----
Use the standard `sphinx-build <http://sphinx-doc.org/invocation.html>`_ syntax.
For the usual case of wanting to generate the documentation in HTML format:

.. code-block:: sh

    sphinx-build -b html . _build

External Files
--------------
reStructuredText not inside the ``docs`` directory hierarchy can't be directly
included in a table of contents.  To include a README.rst file from the
repository's root directory in the generated documentation, create a
placeholder inside the ``docs`` directory which uses an include directive to
pull in its content:

    ``.. include:: ../README.rst``

For an example, see ``docs/readme.rst`` in this project.

PyPI Description Validation
---------------------------
If PyPI encounters something it doesn't know how to handle in a reStructuredText
package description, it just silently shows it as plain text instead of
formatting it as expected.  To get some warning of this before uploading your
package, use the ``validate_readme.py`` script which gets installed along with
sbo-sphinx.  Basic usage is::

    validate_readme.py README.rst

For more details, see the output of ``validate_readme.py -h``.

Markdown
--------
Sphinx currently has no real support for Markdown-style wiki markup.  If a
project has a README.md which you want to include in the documentation, there
are a few options:

* Convert it to README.rst instead, changing the markup accordingly.
  `pandoc <http://johnmacfarlane.net/pandoc/>`_ may do a reasonably good job
  of automating this conversion.
* Add a reStructuredText-formatted copy of the file to the ``docs`` directory
  and include that in the documentation instead.  This does run the risk of
  the copy getting out of sync with the original, however.
* Implement a Sphinx extension which uses pandoc to automatically convert and
  copy the Markdown files specified in a configured list.  The drawback with
  this approach is that it requires pandoc to be installed on each system on
  which the documentation will be generated.

Read the Docs
-------------
sbo-sphinx was written to be mostly compatible with the
`Read the Docs <https://readthedocs.org/>`_ service, but there are still a
couple of gotchas:

* The Read the Docs Sphinx theme `currently doesn't display <https://github.com/snide/sphinx_rtd_theme/pull/69>`_
  an HTML logo specified in the configuration.  Additionally, setting an HTML
  logo with Sphinx 1.2.1 generates a
  `spurious warning <https://bitbucket.org/birkenfeld/sphinx/issue/1352/copying-html_logo-file-over-improperly>`_
  in the build output.  Until at least the first bug is fixed, a logo can
  really only be usefully specified for the LaTeX/PDF output.
* Keep in mind that private source code repositories cannot be used on the
  public Read the Docs service (but can be on a suitably configured private
  installation).

Notes
-----
* The table of contents page for Python modules is generated at
  ``docs/python/index``.  The equivalent file for JavaScript (if generated)
  is at ``docs/javascript/index``, and there is also a list of processed JS
  files at ``docs/javascript/files``.  These should be added to a toctree
  directive in the documentation.  Again, see this project's ``docs/index.rst``
  for an example.
* The RST-Template library for creating reST files from JSDoc comments
  currently uses jsdoc-toolkit, which is no longer in active development.  If
  we decide that its successor JSDoc 3 has enough useful improvements, we can
  look into updating the library to use that instead.

Troubleshooting
---------------
* *error: unrecognized arguments* - If this pops up and breaks the build while
  parsing the code being documented, odds are that file has code at the module
  level which uses ``argparse`` or ``optparse``, and it's unsuccessfully trying
  to parse the command line parameters which were given to sphinx-build.  Put
  such code inside a function which is only called inside an
  ``if __name__ == '__main__'`` condition (i.e., if that script was the one
  called).

References
----------

* `Sphinx <http://sphinx-doc.org/>`_
* `reStructuredText syntax overview <http://docutils.sourceforge.net/docs/user/rst/quickstart.html>`_
* `JSDoc <http://code.google.com/p/jsdoc-toolkit/>`_
* `JSDoc 3 <http://usejsdoc.org/index.html>`_
* `JsDoc Toolkit RST-Template <https://jsdoc-toolkit-rst-template.readthedocs.org/en/latest/index.html>`_
* `sphinx-contrib <https://bitbucket.org/birkenfeld/sphinx-contrib>`_ - Lots of
  cool stuff here; support for CoffeeScript, Doxygen, Erlang, Excel, Google
  charts and maps, RESTful HTTP APIs, Ruby, etc.
* `sphinxcontrib.httpdomain <http://packages.python.org/sphinxcontrib-httpdomain/>`_ - Documenting RESTful HTTP APIs
