Welcome to `scal`'s documentation!
==================================

|sources| |pypi| |documentation| |license|

I use this program about once a year to print a one-page school-year
calendar. But it can be used to represent any calendar.

It is heavily inspired by the simple yet powerful Robert Krause's `calendar
<http://www.texample.net/tikz/examples/a-calender-for-doublesided-din-a4/>`_,
itself using the complex yet powerful Till Tantau's `TikZ
<http://www.ctan.org/pkg/pgf>`_ LaTeX package.

Examples:

- French school year:

  - 2014-2015:
    :download:`zone A <examples/fr_20142015_A.pdf>` (:download:`source <examples/fr_20142015_A.scl>`),
    :download:`zone B <examples/fr_20142015_B.pdf>` (:download:`source <examples/fr_20142015_B.scl>`),
    :download:`zone C <examples/fr_20142015_C.pdf>` (:download:`source <examples/fr_20142015_C.scl>`)

  - 2015-2016:
    :download:`zone A <examples/fr_20152016_A.pdf>` (:download:`source <examples/fr_20152016_A.scl>`),
    :download:`zone B <examples/fr_20152016_B.pdf>` (:download:`source <examples/fr_20152016_B.scl>`),
    :download:`zone C <examples/fr_20152016_C.pdf>` (:download:`source <examples/fr_20152016_C.scl>`)

  - 2016-2017:
    :download:`zone A <examples/fr_20162017_A.pdf>` (:download:`source <examples/fr_20162017_A.scl>`),
    :download:`zone B <examples/fr_20162017_B.pdf>` (:download:`source <examples/fr_20162017_B.scl>`),
    :download:`zone C <examples/fr_20162017_C.pdf>` (:download:`source <examples/fr_20162017_C.scl>`)

Download and install
--------------------

See the `main project page <http://git.framasoft.org/spalax/scal>`_ for
instructions.

Usage
-----

Here are the command line options for `scal`.

.. argparse::
    :module: scal.options
    :func: commandline_parser
    :prog: scal

Note that `scal` only produce the XeLaTeX code corresponding to the calendar. To get the `pdf` calendar, save the code as a :file:`.tex` file, or pipe the output through `xelatex`:

.. code-block:: bash

    scal FILE | xelatex

Configuration file
------------------

The file given in argument contains the information about the calendar. Here
is, for example, the file corresponding to a school year calendar.

.. literalinclude:: examples/fr_20142015_B.scl

The file is parsed line per line, the following way.

- The ``#`` character starts a comment: it, and everything following it, are ignored.
- Blank lines are ignored.
- The date format is ``YYYY-MM-DD`` (or ``MM-DD`` in some cases).
- Start and end date of the calendar are set by a line ``From STARTDATE to ENDDATE``.
- The base command to define a holiday is ``STARTDATE ENDDATE NAME``, where ``STARTDATE`` and ``ENDDATE`` are the first and last days of the holiday, and ``NAME`` is the holiday name (as a XeLaTeX code), to be displayed on the calendar.

  - ``NAME`` can be omitted;
  - ``STARTDATE`` can be omitted for a one-day vacation (e.g. ``2015-04-05 Easter``);
  - The year can be omitted if the vacation happens every year (e.g. ``05-01 Labour day``).

- Moreover, the following configuration variables can be set, as ``VARIABLE = VALUE``:

  - ``papersize``: Paper size (this string must be recognized by the `geometry <http://www.ctan.org/pkg/geometry>`_ LaTeX package).
  - ``lang``: Language of the calendar (this string must be recognized by the `polyglossia <http://www.ctan.org/pkg/polyglossia>`_ LaTeX package).

Indices and tables
------------------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

.. |documentation| image:: http://readthedocs.org/projects/scal/badge
  :target: http://scal.readthedocs.org
.. |pypi| image:: https://img.shields.io/pypi/v/scal.svg
  :target: http://pypi.python.org/pypi/scal
.. |license| image:: https://img.shields.io/pypi/l/scal.svg
  :target: http://www.gnu.org/licenses/gpl-3.0.html
.. |sources| image:: https://img.shields.io/badge/sources-scal-brightgreen.svg
  :target: http://git.framasoft.org/spalax/scal
