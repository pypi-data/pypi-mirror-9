Release process
===============

- Tests

  - Test with current python version::

      python setup.py test

  - Test with all supported versions::

      tox

- Bump version number, and commit this, in files:

  - setup.py
  - scal/__init__.py
  - ``grep -Ri <current_version>`` to be sure not to forget anything.

- Test publishing:

  - Build: ``python setup.py sdist``
  - Documentation should build: https://readthedocs.org/builds/scal/
  - README should be correctly rendered: https://git.framasoft.org/spalax/scal

- Create a git tag::

    git tag v<version>

- Publish::

    git push
    git push --tags
    python setup.py sdist register upload

