Welcome to `cahier`'s documentation!
====================================

One-directory-a-day calendar management

.. note::

  I am no longer using this software, so it will not be improved. Feel free to
  ask questions and to submit bugs anyway, but this will not be my priority.

  -- Louis

Rationale
---------

*Note that althougt I wrote this program for this particular purpose, I had
extensibility in mind. Please read on the usage and configuration sections
before deciding that this program does not fit your needs.*

As a part of my job as a teacher, I have to log my work on a daily basis
(*cahier de textes* in French, hence the name). To do so, I use `IkiWiki
<http://ikiwiki.info>`_. Each entry is stored in a markdown file named
`YYYYMMDD.mdwn`, and each attached document is located in the `YYYYMMDD`
directory. So, after a few days, an ``ls`` gives:

.. code-block:: console

  $ ls
  20130906       20130927.mdwn   20131018b       20131122        20131217.mdwn
  20130906.mdwn  20130930.mdwn   20131018b.mdwn  20131122.mdwn   20131218.mdwn
  20130909.mdwn  20131001.mdwn   20131104.mdwn   20131125.mdwn   20131220
  20130910.mdwn  20131002        20131105        20131126.mdwn   20131220.mdwn
  20130911.mdwn  20131002.mdwn   20131105.mdwn   20131127.mdwn   20140107.mdwn
  20130913.mdwn  20131004.mdwn   20131106.mdwn   20131129a.mdwn  20140108.mdwn
  20130916.mdwn  20131007.mdwn   20131108        20131129b.mdwn  20140110
  20130917       20131008        20131108.mdwn   20131202.mdwn   20140110.mdwn
  20130917.mdwn  20131008.mdwn   20131112        20131203        20140113.mdwn
  20130918       20131009.mdwn   20131112.mdwn   20131203.mdwn   20140114.mdwn
  20130918.mdwn  20131011        20131113a.mdwn  20131204.mdwn   20140115
  20130920       20131011.mdwn   20131113b.mdwn  20131206.mdwn   20140115.mdwn
  20130920.mdwn  20131014.mdwn   20131115        20131209.mdwn   20140117
  20130923.mdwn  20131015.mdwn   20131115.mdwn   20131210.mdwn   20140117.mdwn
  20130924       20131016        20131118.mdwn   20131211        20140120.mdwn
  20130924.mdwn  20131016.mdwn   20131119.mdwn   20131211.mdwn   20140121.mdwn
  20130925.mdwn  20131018a       20131120        20131213.mdwn   20140122
  20130927       20131018a.mdwn  20131120.mdwn   20131216.mdwn   20140122.mdwn

There are several problems.

- Command line completion is broken: file names are so close that it is almost
  useless:

  - typing in the file name to edit it is frustrating;
  - typing in the directory name to create it is frustrating;
  - typing in the directory name to move a file to it is frustrating.

- When editing the file, I have to fill the date and time of the calendar
  entry, although this information is contained in the file name, and could be
  guessed (my timetable does not change from one week to another).

- I have different classes, with different calendar, and I want the right class
  to be automatically taken into account.

I wrote this program to automate this task.

Download and install
--------------------

See the `main project page <http://git.framasoft.org/spalax/cahier>`_ for
instructions.

Usage and configuration
-----------------------

Base commands
"""""""""""""

The base commands operate on the *right* calendar, with the *right* date.

- The *right* calendar is determined using profiles (more information in section
  :ref:`profiles`). In this configuration, you can associate several
  directories to one calendar. For instance, if I associate directory
  :file:`~/courses/cs` with calendar :file:`~/calendars/cs101`, a ``cahier``
  command run in :file:`~/courses/cs` (or any of its subdirectories) will
  consider the associated calendar. This is useful if you have several
  calendars.
- The *right* date is also configured in the profiles. You can register a
  simplified version of your time table, so that when editing a new entry, its
  date is calculated using this time table, and the appropriate date and time
  is filled in the template.

The base commands are (a full list of commands is available in section
:ref:`command`).

- ``cahier new``
  Create a new entry, at the right place, with the right date, and start
  editing it.

- ``cahier edit``
  Edit the last created entry.

- ``cahier attach``
  Attach a file to the last entry, that is:

  - create the directory if necessary;
  - proprocess files if relevant: for instance, I want command ``cahier attach
    foo.tex`` to compile :file:`foo.tex` as a pdf, and attach the resulting
    pdf;
  - copy the files in this directory.

- ``cahier cd``
  Start a shell in the calendar directory

- ``cahier wiki``
  Arguments to this command are passed to ``ikiwiki``, in the calendar
  directory. More options are available as well, like ``cahier refresh`` which
  compile the wiki (whatever the working directory is).

- ``cahier git``
  Arguments to this command are passed to ``git``, called in the calendar
  directory.


Configuration
"""""""""""""

.. _stringformatting:

String formatting
^^^^^^^^^^^^^^^^^

Strings of configuration files are formatted in two ways.

- They are formatted according to the rules of the `configparser
  <http://docs.python.org/3.4/library/configparser.html>`_ module.
- They are formatted, using the ``{key}`` format, with the following values:

  - ``basename``: basename of the edited file (without directory nor extension);
  - ``configdir``: ``cahier`` configuration directory;
  - ``dirname``: directory of edited file;
  - ``filename``: like basename, with the extension.

General configuration
^^^^^^^^^^^^^^^^^^^^^

General configuration is set in file :file:`.cahier/cahier.cfg`. Example:

.. code-block:: cfg

  [options]
  casesensitive: no

  [bin]
  editor: screen -t "$EDITOR" sh -c "(cd {dirname} && $EDITOR {filename})"
  shell: screen

  [wiki]
  options: --verbose --no-rcs
  fileformat: %%Y%%m%%d
  fileformat-length: 8
  template: {configdir}/templates/template.mdwn

- ``options``:

  - ``casesensitive``: Set whether profile names are case sensitive or not.

- ``bin``:

  - ``editor``: Command to call to edit files.
  - ``shell``: Shell to invoke with ``cahier cd``.

- ``wiki``:

  - ``options``: Options used when calling ``ikiwiki``.
  - ``fileformat-length``: Length of date in the file names (e.g. if your file names are `YYYYMMDD-foo`, ``fileformat-length`` will be 8; if your file names are `MMDD-foo`, ``fileformat-length`` will be 4).
  - ``fileformat``: Date format of files, as recognized by the `datetime.strptime() <http://docs.python.org/2/library/datetime.html#datetime.datetime.strptime>`_ function.
  - ``template``: Template to use for newly created files.

.. _profiles:

Profiles
^^^^^^^^

Profile configuration is set in :file:`.cahier/profiles/NAME.cfg`. Example:

.. code-block:: cfg

  [DEFAULT]
  ikiwiki: ~/prof/1S3/cahier

  [options]
  workdays: monday:08 tuesday:09 wednesday:08 friday:15:30

  [config]
  setup: %(ikiwiki)s/wiki.setup

  [directories]
  calendar: %(ikiwiki)s/seances
  sources: ~/prof/1S-math ~/prof/1S3

- ``DEFAULT``: Default values for all sections.

  - ``ikiwiki``: This is an example of a trick taking advantage of :ref:`string
    formatting <stringformatting>` to factorize configuration: the
    ``%(ikiwiki)s`` part in following options are replaced by value of this
    string.

- ``options``:

  - ``workdays``: Timetable, with times. This is a space separated list of
    `DAY:HOUR`. If this option is set, when editing a new file, the following
    date corresponding to one of those work days is used as the date.
    Otherwise, the current date and time is used.

- ``config``:

  - ``setup``: Path to the IkiWiki setup file.

- ``directories``:

  - ``calendar``: Path to the directory containing the calendar files.
  - ``sources``: Paths associated to this profile. When calling ``cahier`` in
    one of those directory, the corresponding profile is used.

File plugins
^^^^^^^^^^^^

File plugins are configured in files :file:`.cahier/ftplugins/EXTENSION.cfg`
(where `EXTENSION` is the extension of files impacted by this particular
configuration file).

.. code-block:: cfg

  [preprocess]
      cmd: pdflatex {basename}
      name: {basename}.pdf

- ``preprocess``: Commands to preprocess files before attaching them. For
  instance, with this example, LaTeX files are compiled, and their compiled
  version is attached to the current date.

  - ``cmd*``: Values of keys starting with ``cmd`` are executed before
    attaching files.
  - ``name``: Name of the file to attach, if different from the base file name.

File templates
^^^^^^^^^^^^^^

Files :file:`.cahier/templates/template.foo` are used as templates when editing
a new file of type ``foo``. Type is the extension of the file.

Template content is formatted as a Python string, with only one variable:

- ``date``: the date and time of the log of the created file.

.. _command:

Full command line options
"""""""""""""""""""""""""

Here are the command line options for `cahier`.

.. argparse::
    :module: cahier.main
    :func: commandline_parser
    :prog: cahier

Indices and tables
------------------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

