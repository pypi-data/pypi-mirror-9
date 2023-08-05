mincss
======

.. image:: https://travis-ci.org/peterbe/mincss.png?branch=master
    :target: https://travis-ci.org/peterbe/mincss
    :alt: Build status

Clears the junk out of your CSS by finding out which selectors are
actually not used in your HTML.

By Peter Bengtsson, 2012-2015

Tested in Python 2.7, 3.3 and 3.4

Example
-------

::

    $ mincss https://github.com


Installation
------------

From pip::

    $ pip install mincss

Why?
----

With the onslaught of Twitter Bootstrap upon the world it's very
tempting to just download their whole fat 80+Kb CSS and serve it up even
though you're not using half of the HTML that it styles.

There's also the case of websites that have changed over time but
without the CSS getting the same amount of love refactoring. Then it's
very likely that you get CSS selectors that you're no longer or never
using.

This tool can help you get started reducing all those selectors that
you're not using.

Whitespace compression?
-----------------------

No, that's a separate concern. This tool works independent of whitespace
compression/optimization.

For example, if you have a build step or a runtime step that converts
all your CSS files into one (concatenation) and trims away all the
excess whitespace (compression) then the output CSS can still contain
selectors that are never actually used.

What about AJAX?
----------------

If you have a script that creates DOM elements in some sort of
``window.onload`` event then ``mincss`` will not be able to know this
because at the moment ``mincss`` is entirely static.

So what is a web developer to do? Simple, use ``/* no mincss */`` like
this for example:

::

    .logged-in-info {
        /* no mincss */
        color: pink;
    }

That tells ``mincss`` to ignore the whole block and all its selectors.
