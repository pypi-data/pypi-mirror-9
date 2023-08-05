# -*- coding: utf-8 -*-
r"""ANSI Color formatting for output in terminal.

Access to ansi sequences
------------------------

Access to raw ANSI color sequence can be done via FG, BG, ATTR, and
CTL attritbutes dicts::

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

    >>> "Hmm" + FG.red + "Hello" + FG.default + "you."
    'Hmm\x1b[31mHello\x1b[39myou.'

And print it.


high level ansi management
--------------------------

As this documentation is intended to be printed in various format which
most of them are not ANSI compatible, and for debugging purpose, ANSI chars
should be explicit, we have a simple object which replaces the ANSI string
conveniently and has a 'repr' which is explicit:

    >>> fg.red
    '{fg.red}'
    >>> str(fg.red)
    '\x1b[31m'

This works for all 4 namespaces:

    >>> fg.black, bg.blue, attr.bold, ctl.reset
    ('{fg.black}', '{bg.blue}', '{attr.bold}', '{ctl.reset}')

More over, traditional addition, join and interpolation still work:

    >>> "hello " + fg.red + "you" + fg.default
    'hello \x1b[31myou\x1b[39m'

    >>> "hello %syou%s" % (fg.red, fg.default)
    'hello \x1b[31myou\x1b[39m'

    >>> "".join(["hello ", fg.red, "you", fg.default])
    'hello \x1b[31myou\x1b[39m'


Notice that ``aformat`` is somewhat clever ::

    >>> you = aformat("You", fg="red")
    >>> aformat("Hello, Are " + you + " Well", fg="blue")
    aformat('\x1b[34mHello, Are \x1b[31mYou\x1b[34m Well\x1b[39m')

Notice how the ending ansi sequence of the ``you`` sets back the blue
color and not the default one. So the word "Well" still appears in blue.

``aformat`` is clever, but with some limitation, hitting mainly string
interpolation::

    >>> aformat("Hello, Are %s Well" % you, fg="blue")
    aformat('\x1b[34mHello, Are \x1b[31mYou\x1b[39m Well\x1b[39m')

"""

import os
import re

## ref: http://en.wikipedia.org/wiki/ANSI_escape_code
_ATTR = '? bold faint italic underline blink ? reverse conceal strike'
_COLORS = 'black red green yellow blue magenta cyan white ? default'
_CTL = 'reset'

CSI = '\033['
ANSI_SGR = '%dm'


class attrdict(dict):
    def __init__(self, *args, **kwargs):
        super(attrdict, self).__init__(*args, **kwargs)
        self.__dict__ = self


def label2code(labels, offset):
    return attrdict(
        (label, CSI + (ANSI_SGR % (offset + idx)))
        for idx, label in enumerate(labels.split())
        if label != "?")


ATTR = label2code(_ATTR, offset=0)
_UNATTR = re.sub(r'(\w+)', 'un\\1', _ATTR)
ATTR.update(label2code(_UNATTR, offset=20))


FG = label2code(_COLORS, offset=30)
BG = label2code(_COLORS, offset=40)
CTL = label2code(_CTL, offset=0)


##
## High level
##

invert_attr_label = lambda l, dct: l[2:] if l[2:] in dct else "un%s" % l


class ANSIEscape(str): pass


def ANSIEscapeFactory(name, dct):
    def _mk(label, dct):
        class _ANSIEscape(ANSIEscape): pass
        _ANSIEscape.__repr__ = lambda s: repr('{%s.%s}' % (name, s.label))
        e = _ANSIEscape(dct[label])
        e.label = label
        inv = invert_attr_label(label, dct)
        if inv in dct:
            _ANSIEscape.__inv__ = lambda s: _mk(inv, dct)
        return e
    return attrdict((label, _mk(label, dct)) for label in dct)


lvars = locals()
attr = fg = bg = ctl = None
for ns in "attr fg bg ctl".split():
    lvars[ns] = ANSIEscapeFactory(ns, lvars[ns.upper()])


##
## Boxing attributes (keeping state of attributes)
##

invert_attr_label = lambda l, dct: l[2:] if l[2:] in dct else "un%s" % l


def state_change(sa, sb):
    """Returns ansi escape sequence list to switch state sa to sb

    >>> state_change({"fg": "blue"}, {"fg": "default"})
    ['{fg.default}']

    >>> state_change({"fg": "blue", "bg": "yellow"},
    ...              {"fg": "blue", "bg": "default"})
    ['{bg.default}']

    >>> state_change({"attrs": ["bold", ]}, {"attrs": ["italic", ]})
    ['{attr.italic}', '{attr.unbold}']

    """
    global attr
    s_color = [globals()[k.lower()][sb[k]]
               for k in "fg bg".split()
               if sa.get(k, "default") != sb.get(k, "default")]
    sa_attrs, sb_attrs = set(sa.get("attrs", [])), set(sb.get("attrs", []))
    s_attrs = [attr[a] for a in sb_attrs - sa_attrs]
    s_unattrs = [attr[invert_attr_label(a, attr)]
                 for a in sa_attrs - sb_attrs]
    return s_color + s_attrs + s_unattrs


def get_new_state(current, defs):
    """Return new state by applying new specs on to current state

    >>> from pprint import pprint as pp
    >>> get_new_state({'fg': 'red'}, {'fg': 'blue'})
    {'fg': 'blue'}

    >>> pp(get_new_state({'fg': 'red'}, {'bg': 'blue'}))
    {'bg': 'blue', 'fg': 'red'}

    >>> pp(get_new_state({'attrs': ['bold', ]}, {'attrs': ['unbold',]}))
    {'attrs': []}

    >>> pp(get_new_state({'attrs': ['bold', ]}, {'attrs': ['unitalic',]}))
    {'attrs': ['bold', 'unitalic']}

    """
    new_state = current.copy()
    if defs.get('attrs', []):
        for a in defs["attrs"]:
            ia = invert_attr_label(a, ATTR)
            if ia in new_state["attrs"]:
                new_state["attrs"].remove(ia)
            else:
                new_state["attrs"].append(a)
    for l in "fg bg".split():
        if defs.get(l, None):
            new_state[l] = defs[l]
    return new_state


mk_or_str = lambda s, ps: s.fmt(ps) if isinstance(s, ANSITextExpr) \
                          else ("%s" % s)


class ANSITextExpr(object):

    def __init__(self, fg=None, bg=None, attrs=None):
        self.fg = fg
        self.bg = bg
        self.attrs = attrs or []

    def fmt(self, prev_state):
        new_state = get_new_state(
            prev_state,
            {"fg": self.fg, "bg": self.bg, "attrs": self.attrs})
        setup = "".join(state_change(prev_state, new_state))
        close = "".join(state_change(new_state, prev_state))
        s = self.mk(new_state)
        return setup + s + close

    def mk(self, prev_state):
        """Return a string from subparts"""
        raise NotImplementedError()

    def __repr__(self):
        return ("aformat(%r)"
                % (str(self)))

    def __str__(self):
        return self.fmt(prev_state={
            'fg': 'default',
            'bg': 'default',
            'attrs': [],
        })

    __add__ = lambda s, v: ANSITextPair(s, v)
    __radd__ = lambda s, v: ANSITextPair(v, s)
    __mod__ = lambda s, v: ANSITextInterpolation(s, v)
    __rmod__ = lambda s, v: ANSITextInterpolation(v, s)


class ANSITextAtom(ANSITextExpr):

    def __init__(self, text, fg=None, bg=None, attrs=None):
        self.text = text
        ANSITextExpr.__init__(self, fg, bg, attrs)

    def mk(self, prev_state):
        """Return a string from subparts"""
        return mk_or_str(self.text, prev_state)


class ANSITextPair(ANSITextExpr):

    def __init__(self, car, cdr, fg=None, bg=None, attrs=None):
        ANSITextExpr.__init__(self, fg, bg, attrs)
        self.car = car
        self.cdr = cdr

    def mk(self, prev_state):
        return mk_or_str(self.car, prev_state) + \
               mk_or_str(self.cdr, prev_state)


class ANSITextInterpolation(ANSITextExpr):

    def __init__(self, text, data, fg=None, bg=None, attrs=None):
        ANSITextExpr.__init__(self, fg, bg, attrs)
        self.text = text
        self.data = data

    def mk(self, prev_state):
        return (mk_or_str(self.text, prev_state)
                % (tuple(mk_or_str(e, prev_state) for e in self.data)
                   if isinstance(self.data, tuple) else
                   mk_or_str(self.data, prev_state)))


aformat = ANSITextAtom
