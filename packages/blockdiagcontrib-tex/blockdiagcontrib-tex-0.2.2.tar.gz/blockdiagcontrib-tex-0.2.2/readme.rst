====================
blockdiagcontrib-tex
====================

Usage
=====

This project provides plugin for embedding LaTeX source into blockdiag.

For example,

::

    blockdiag{
        plugin tex;
        A[label="tex://
            \underline{Thm1}:
            \[
                a^2 + b^2 = c^2.
            \]
        ", resizable=True]
    }

Requirements
============

*  blockdiag 1.4.2 or latter
*  LaTeX
*  dvipng

License
=======

Apache License 2.0

Note
====

This project is inspired of
`blockdiagcontrib-math <https://pypi.python.org/pypi/blockdiagcontrib-math/>`_ .

