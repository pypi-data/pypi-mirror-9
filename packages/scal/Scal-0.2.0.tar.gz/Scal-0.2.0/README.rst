scal — School year calendar generator
=====================================

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
    `zone A <http://scal.readthedocs.org/en/latest/_downloads/fr_20142015_A.pdf>`_ (`source <http://scal.readthedocs.org/en/latest/_downloadss/fr_20142015_A.scl>`_),
    `zone B <http://scal.readthedocs.org/en/latest/_downloads/fr_20142015_B.pdf>`_ (`source <http://scal.readthedocs.org/en/latest/_downloadss/fr_20142015_B.scl>`_),
    `zone C <http://scal.readthedocs.org/en/latest/_downloads/fr_20142015_C.pdf>`_ (`source <http://scal.readthedocs.org/en/latest/_downloadss/fr_20142015_C.scl>`_)

  - 2015-2016:
    `zone A <http://scal.readthedocs.org/en/latest/_downloads/fr_20152016_A.pdf>`_ (`source <http://scal.readthedocs.org/en/latest/_downloadss/fr_20152016_A.scl>`_),
    `zone B <http://scal.readthedocs.org/en/latest/_downloads/fr_20152016_B.pdf>`_ (`source <http://scal.readthedocs.org/en/latest/_downloadss/fr_20152016_B.scl>`_),
    `zone C <http://scal.readthedocs.org/en/latest/_downloads/fr_20152016_C.pdf>`_ (`source <http://scal.readthedocs.org/en/latest/_downloadss/fr_20152016_C.scl>`_)

  - 2016-2017:
    `zone A <http://scal.readthedocs.org/en/latest/_downloads/fr_20162017_A.pdf>`_ (`source <http://scal.readthedocs.org/en/latest/_downloadss/fr_20162017_A.scl>`_),
    `zone B <http://scal.readthedocs.org/en/latest/_downloads/fr_20162017_B.pdf>`_ (`source <http://scal.readthedocs.org/en/latest/_downloadss/fr_20162017_B.scl>`_),
    `zone C <http://scal.readthedocs.org/en/latest/_downloads/fr_20162017_C.pdf>`_ (`source <http://scal.readthedocs.org/en/latest/_downloadss/fr_20162017_C.scl>`_)

Download and install
--------------------

See the end of list for a (quick and dirty) Debian package.

* Non-Python dependencies.
  This program produces XeLaTeX code, but does not compile it. So, LaTeX is not
  needed to run this program. However, to compile the generated code, you will
  need a working LaTeX installation, with ``xelatex``, and XeLaTeX packages
  `geometry <http://www.ctan.org/pkg/geometry>`_,
  `polyglossia <http://www.ctan.org/pkg/polyglossia>`_,
  `tikz <http://www.ctan.org/pkg/pgf>`_,
  `xunicode <http://www.ctan.org/pkg/xunicode>`_,
  `fontspec <http://www.ctan.org/pkg/fontspec>`_,
  and `translator` (provided by the `beamer <http://www.ctan.org/pkg/beamer>`_ package).
  Those are provided by `TeXLive <https://www.tug.org/texlive/>`_ on GNU/Linux,
  `MiKTeX <http://miktex.org/>`_ on Windows, and `MacTeX
  <https://tug.org/mactex/>`_ on MacOS.

* From sources:

  * Download: https://pypi.python.org/pypi/scal
  * Install (in a `virtualenv`, if you do not want to mess with your distribution installation system)::

        python3 setup.py install

* From pip::

    pip install scal

* Quick and dirty Debian (and Ubuntu?) package

  This requires `stdeb <https://github.com/astraw/stdeb>`_ to be installed::

      python3 setup.py --command-packages=stdeb.command bdist_deb
      sudo dpkg -i deb_dist/python3-<VERSION>_all.deb

Documentation
=============

* The compiled documentation is available on `readthedocs
  <http://scal.readthedocs.org>`_

* To compile it from source, download and run::

      cd doc && make html


.. |documentation| image:: http://readthedocs.org/projects/scal/badge
  :target: http://scal.readthedocs.org
.. |pypi| image:: https://img.shields.io/pypi/v/scal.svg
  :target: http://pypi.python.org/pypi/scal
.. |license| image:: https://img.shields.io/pypi/l/scal.svg
  :target: http://www.gnu.org/licenses/gpl-3.0.html
.. |sources| image:: https://img.shields.io/badge/sources-scal-brightgreen.svg
  :target: http://git.framasoft.org/spalax/scal
