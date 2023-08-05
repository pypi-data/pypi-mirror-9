﻿====
EWMH
====

EWMH (Extended Window Manager Hints) can be used to retrieve and set
information about windows on Linux systems. Is does this by calling and
parsing the output from programs like ``wmctrl``.

Example
=======

::

  from subprocess import Popen
  from ruamel.ewmh import ExtendedWindowManagerHints as EWMH
  Popen(['xclock', '-name', 'test_xclock'])
  # there can be more than one window matching the title
  # therfore .by_title() returns a list
  clk = EWMH().by_title('test_xclock')[0]
  clk.resize_and_move(200, 200, 300, 600)


Why not use the ``wmctrl`` package?
===================================

Before writing this library I tried Antonio Cuni's ``wmctrl`` package. That
library looks to be abandoned (at least from April 2013 until Oct 2014).

I started ``ewmh`` because I encountered performance problems and irregular
exceptions that I could not, initially fix. When I noticed that these problems
were a result of design decisions, were associated with features I did not
need (e.g. retrieving WM_CLASS), and because I needed something more minimal,
but working, I started from scratch.

- ``wmctrl`` output information did not get cached and getting the
  information was horrible slow in the first place. If your machine has M
  windows open and you wanted the state for N of those windows, this caused a
  total of N * (M+1) invocations of external programs through
  ``commands.getoutput``. With 200+ open windows on my system, getting
  information took several seconds **for each window** that I was interested
  in.

- ``commands.getoutput()`` is used, but that has been `deprecated since 2008
  <https://docs.python.org/2/library/commands.html>`_, should have used
  ``subprocess.checkout_output()`` instead.

- the output of ``getoutput()`` was not checked for errors.

- ``os.system()`` was used resulting in an unnecessary shell invocation.

- the ``xprop`` program was called **for every window open on the system**,
  although, often, none of that information is used.

- to activate windows the package calls ``wmctrl`` with ``wmctrl -id -a <ID>``,
  I was not sure what the `d` there is supposed to do, without it the command
  has the same effect/output.

After trying to patching some of these issues, and testing, exceptions would happen which forced me to abandon it, as it was less time consuming to start from scratch. With the knowledge gained writing ``emwh`` I found that the wmctrl package currently at least doesn't handle window classes with spaces in them, nor does a program survive calling the library when there happens to be a *window without a title* somewhere on your desktop.

Most of the original tests included with the ``wmctrl`` library, work with only
minor adjustments (which seem to have to do with my top-of-the-window menu)
and a wrapper class in ``emwh``. Moving from ``wmctrl`` to ``ewmh`` should
therefore be easy.
