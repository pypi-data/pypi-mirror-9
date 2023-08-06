stlsort
=======

.. image:: https://badge.fury.io/py/stlsort.svg
    :target: http://badge.fury.io/py/stlsort

.. image:: https://pypip.in/d/stlsort/badge.png
        :target: https://pypi.python.org/pypi/stlsort

Some tools such as OpenSCAD produce randomly ordered STL files so source control like git can't tell if they have changed or not.
This tool orders each triangle to start with the lowest vertex first (comparing x, then y, then z).
It then sorts the triangles to start with the one with the lowest vertices first (comparing first vertex, second, then third).
This has no effect on the model but makes the STL consistent. I.e. it makes a canonical form.

Sort your STL files before committing changes! Add a pre-commit hook like this:


.. code:: sh

    #!/bin/sh
    # This was not tested with filenames containing spaces
    files=`git diff --cached --name-only --diff-filter=ACM | grep .stl$ | tr '\n' ' '`
    if [[ x"$files" != x ]]; then
      stlsort $files
      git add $files
    fi

This was created by nop head as a part of `Mendel90 <https://github.com/nophead/Mendel90>`_ repository. Works only for ASCII STLs (convert your STLs from binary to ASCII in pre-commit hook if needed).
