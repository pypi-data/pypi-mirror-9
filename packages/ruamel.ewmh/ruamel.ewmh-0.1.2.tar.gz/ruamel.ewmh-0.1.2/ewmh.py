# coding: utf-8

"""
EWMH window management
"""

from __future__ import print_function

import sys
import subprocess


from . import __version__


class Window:
    def __init__(self, ewmh, wid, workspace, pid, x, y, w, h, hostname, title):
        self.ewmh = ewmh
        self.wid = wid
        self.workspace = workspace
        self.pid = pid
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.hostname = hostname
        self.title = title
        self._class = None
        self._role = None

    @property
    def cls(self):
        """class requires the invocation of a second wmctrl with -x to get
        WM_CLASS. This is not included in the first call to wmctrl, as
        the class name can have spaces and that makes splitting the output
        difficult. On the first access of this property, **all windows**
        have their ._class attribute updated.
        """
        if self._class is None:
            self.ewmh._add_class()
            print ('cls2', self._class)
        return self._class

    @property
    def wm_name(self):
        return self.title

    @property
    def wm_class(self):
        x = self.cls
        print ('x', x)
        return self.cls

    @property
    def id(self):
        return self.wid

    def activate(self):
        subprocess.check_output(['wmctrl', '-i', '-a', (self.wid)])

    def resize_and_move(self, x, y, w, h):
        import os
        mvarg = '0,%d,%d,%d,%d' % (x, y, w, h)
        subprocess.check_output([
            'wmctrl', '-i', '-r', str(self.wid), '-e', mvarg])

    def to_desktop(self, desktop_id):
        subprocess.check_output([
            'wmctrl', '-i', '-r', (self.wid), '-t', str(desktop_id)])

    def add_skip_taskbar(self):
        subprocess.check_output([
            'wmctrl', '-i', '-r', str(self.wid), '-b', 'add,skip_taskbar'])

    def set_geometry(self, geometry):
        dim, pos = geometry.split('+', 1)
        w, h = map(int, dim.split('x'))
        x, y = map(int, pos.split('+'))
        self.resize_and_move(x, y, w, h)

    @property
    def role(self):
        if self._role is not None:
            return self._role
        self._role = ''
        out = subprocess.check_output(
            ['xprop', '-id', self.wid, 'WM_WINDOW_ROLE'])
        try:
            _, value = out.split(' = ')
        except ValueError:
            # probably xprop returned an error
            return ''
        else:
            self._role = value.strip('"')
        return self._role


class ExtendedWindowManagerHints:
    _names = 'wid workspace pid x y w h hostname title'.split()

    def __init__(self):
        self._windows = None

    def by_id(self, id):
        """return a window by its id
        id is a string 0x.. as returned in the first field of wmctrl -l output
        """
        if self._windows is None:
            _ = self.windows  # read if not there
        return self._windows[id]

    def by_title(self, title, start=False, end=False):
        if start:
            return [w for w in self.windows if w.title.startswith(title)]
        if end:
            return [w for w in self.windows if w.title.endswith(title)]
        return [win for win in self.windows if win.title == title]

    def by_role(self, role):
        return [win for win in self.list() if win.wm_window_role == role]

    def by_class(self, wm_class):
        return [win for win in self.list() if win.wm_class == wm_class]

    @property
    def windows(self):
        if self._windows is None:
            self._scan()
        return self._windows.values()

    @windows.deleter
    def windows(self):
        self._windows = None

    def _scan(self):
        self._windows = {}
        NR_PARTS = 8
        res = subprocess.check_output('wmctrl -l -G -p'.split())
        for line in res.splitlines():
            parts = line.split(None, NR_PARTS)
            wid = parts[0]
            assert wid not in self._windows
            parts = [self, parts[0]] + [int(x) for x in parts[1:NR_PARTS-1]] + \
                [z.decode('utf-8') for z in parts[NR_PARTS-1:]]

            # the 'new' seperate download window in Firefox has no name
            if len(parts) == NR_PARTS - 1:
                parts.append('')  # not very helpful for identifying
            w = Window(*parts)
            self._windows[wid] = w

    def _add_class(self):
        """try to find the class name, which can have spaces, so we
           need to be careful extracting it.
           Triggered by Window.cls access"""
        res = subprocess.check_output('wmctrl -l -G -p -x'.split())
        for line in res.decode('utf-8').splitlines():
            wid, rest = line.split(None, 1)
            try:
                window = self._windows[wid]
            except KeyError:
                continue
            # split the line on the hostname
            rest = rest.split(' ' + window.hostname + ' ', 1)[0]
            # take away the first 7 items, class name can have spaces
            window._class = rest.split(None, 7)[-1]

    @property
    def active(self):
        out = subprocess.check_output("xprop -root _NET_ACTIVE_WINDOW".split())
        parts = out.split()
        try:
            id = parts[-1]
        except ValueError:
            return None
        _ = self.windows
        for w in self.windows:
            print(w.title)
        print('parts', parts, repr(id))
        lst = self._windows.get(id)
        if not lst:
            print('no list')
            return None
        assert len(lst) == 1
        return lst[0]

EWMH = ExtendedWindowManagerHints


class AltExtendedWindowManagerHints(ExtendedWindowManagerHints):
    """for some compatibility with wmctrl.Window"""
    def __init__(self):
        pass

    @classmethod
    def list(cls):
        return ExtendedWindowManagerHints().windows

    @classmethod
    def by_name(cls, name):
        return [win for win in cls.list() if win.wm_name == name]

    @classmethod
    def get_active(cls):
        return ExtendedWindowManagerHints().active
