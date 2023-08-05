=========================
kids.ansi
=========================

.. image:: https://pypip.in/v/kids.ansi/badge.png
    :target: https://pypi.python.org/pypi/kids.ansi

.. image:: https://secure.travis-ci.org/0k/kids.ansi.png?branch=master
    :target: http://travis-ci.org/0k/kids.ansi


``kids.ansi`` is a Python library providing helpers when writing command
line utilities in python. It's part of 'Kids' (for Keep It Dead Simple)
library, but can be used with no extra dependencies.


Maturity
--------

This code is in alpha stage. Some part of it are ongoing reflexions.
What is documented here shouldn't change much, and is actually working.


Features
--------

using ``kids.ansi``:

- Access and insert ANSI escape sequences manualy.
- Or use the ``aformat`` wrapper for full abstraction.

Note that it's very close to what ``termcolor`` does.


Usage
-----


aformat
"""""""

``kids.ansi`` features a ``aformat`` function to return a string
ready for print with the ansi character inside::

    >>> from kids.ansi import aformat

    >>> aformat("You", fg="red")
    aformat('\x1b[31mYou\x1b[39m')

    >>> aformat("Hello You, how are you?", fg="black", bg="blue", attrs=["bold", ])
    aformat('\x1b[30m\x1b[44mHello You, how are you?\x1b[39m\x1b[49m')

Notice that ``aformat`` is somewhat clever ::

    >>> you = aformat("You", fg="red")
    >>> aformat("Hello, Are " + you + " Well", fg="blue")
    aformat('\x1b[34mHello, Are \x1b[31mYou\x1b[34m Well\x1b[39m')

Notice how the ending ansi sequence of the ``you`` sets back the blue
color and not the default one. So the word "Well" still appears in blue.

``aformat`` is clever, but still with some limitation, hitting mainly
string interpolation::

    >>> aformat("Hello, Are %s Well" % you, fg="blue")
    aformat('\x1b[34mHello, Are \x1b[31mYou\x1b[39m Well\x1b[39m')

The word "Well" is NOT in blue. This is an issue.

Access to ansi sequences
""""""""""""""""""""""""

Access to raw ANSI color sequence can be done via FG, BG, ATTR, and
CTL attritbutes dicts::

    >>> from kids.ansi import FG, BG, ATTR, CTL

    >>> FG.white
    '\x1b[37m'
    >>> BG.red
    '\x1b[41m'
    >>> BG.default
    '\x1b[49m'
    >>> ATTR.bold
    '\x1b[1m'
    >>> ATTR.unbold
    '\x1b[21m'
    >>> CTL.reset
    '\x1b[0m'

As these are dicts, and you don't remember all the accessible keys, you can
introspect them easily::

    >>> sorted(ATTR)  ## doctest: +NORMALIZE_WHITESPACE
    ['blink', 'bold', 'conceal', 'faint', 'italic', 'reverse', 'strike',
     'unblink', 'unbold', 'unconceal', 'underline', 'unfaint', 'unitalic',
     'unreverse', 'unstrike', 'ununderline']

You could then::

    >>> "Hmm " + FG.red + "Hello" + FG.default + " you."
    'Hmm \x1b[31mHello\x1b[39m you.'

And print it.

