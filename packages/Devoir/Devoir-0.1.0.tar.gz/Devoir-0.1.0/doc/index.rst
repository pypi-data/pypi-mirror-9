Welcome to `devoir`'s documentation!
====================================

``devoir`` is a tool aimed at quickly setting up a working environment to edit a file.

Rationale
---------

When editing a LaTeX file, I want the file being edited with `vim
<http://www.vim.org>`_, the compiled file displayed using a pdf viewer, and
latex being run whenever something changes, using `latexmk
<http://users.phys.psu.edu/~collins/software/latexmk-jcc/>`_. But wait, there
is more.

- I often start a LaTeX document by copying an existing one, as a template.
- The pdf file may or may not exist when I start working: if I have already
  been working on this file before, the pdf file exists; if not, it does not
  exists, and my pdf viewer won't start on a non-existing file.

This program aims to automate all this process. I built it to process LaTeX
files, but it should work with other files too.

Download and install
--------------------

See the `main project page <http://git.framasoft.org/spalax/devoir>`_ for
instructions.

Usage
-----

.. argparse::
    :module: devoir.main
    :func: commandline_parser
    :prog: devoir

Configuration
-------------

Configuration file
^^^^^^^^^^^^^^^^^^

Configuration files are placed in directory :file:`~/.devoir/ftplugins`. When
calling ``devoir``, the config file corresponding to the extension of the file
argument is loaded: for instance, calling ``devoir foo.tex`` would load
configuration file :file:`~/.devoir/ftplugins/tex.cfg`.

Here is an example.

.. code-block:: cfg

  [config]
  
  cwd = {dirname}
  
  [process]
  
  pre = test -e {basename}.pdf || cp {configdir}/templates/pdf {basename}.pdf
  cmd1 = evince {basename}.pdf &
  cmd2 = screen $EDITOR {basename}.tex
  cmd3 = screen latexmk -pvc {basename}

The following options are available:

- Section ``config``

  - ``cwd``: commands are called from this directory.

- Section ``process``

  The values of keys are commands to be run, in a shell. Keys are meaningless:
  you can use them to label your commands.

String formatting
^^^^^^^^^^^^^^^^^

All values of the configuration files are formatted with the following
dictionary:

- ``basename``: base name of the edited file (that is, file without its
  directory).
- ``dirname``: absolute directory name of the edited file.
- ``filename`` : filename, as passed to ``devoir``.
- ``configdir``: path of the configuration file used.

Templates
^^^^^^^^^

When editing a file (e.g. ``devoir foo.tex``), a file
:file:`foo.tex` is created before being edited:

- if a ``template`` argument was provided, it is used;
- otherwise, if a :file:`~/.devoir/templates/EXTENSION` file exists, it is used
  (e.g. :file:`~/.devoir/templates/tex`);
- otherwise, create an empty file.

Note that this is compatible with `vim` in two ways:

- When editing an empty file, vim still loads the corresponding (vim) template
  if necessary.
- As templates are identified by their extension, having
  :file:`~/.devoir/templates` be a symbolic link to :file:`~/.vim/templates/`
  should work in many cases.

Indices and tables
------------------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

