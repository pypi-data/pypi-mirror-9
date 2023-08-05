
import subprocess
import time

from ruamel.ewmh import ExtendedWindowManagerHints as EWMH

# derived from Cuni's

class Xchild(object):
    cmd = None
    ARGS = []
    sleep = 0.5

    def __init__(self, *args):
        arglist = [self.CMD, '-name', self.NAME] + list(args)
        self.child = subprocess.Popen(arglist)
        time.sleep(self.sleep)

    def __del__(self):
        self.child.kill()

class Apps:
    class get_xclock(Xchild):
        CMD = 'xclock'
        NAME = 'xclock-for-pytest'

    class get_xfontsel(Xchild):
        CMD = 'xfontsel'
        NAME = 'xfontsel-for-pytest'



class TestEWMH:

    @property
    def ewmh(self):
        """no cashing for multiple window queries"""
        return EWMH()

    def get_win(self, name, *args):
        get_app = getattr(Apps, 'get_%s' % name)
        xapp = get_app(*args)
        win = self.ewmh.by_title(get_app.NAME)
        return win[0], xapp

    def check_geometry(self, geom):
        win, xclock = self.get_win('xclock', '-geometry', geom)
        win.resize_and_move(0, 0, 100, 200)
        win.set_geometry(geom)
        win2 = self.ewmh.by_title(xclock.NAME)[0]
        assert win2.x == win.x
        assert win2.y == win.y
        assert win2.w == win.w
        assert win2.h == win.h

    def test_list(self):
        xclock = Apps.get_xclock()
        names = [win.title for win in self.ewmh.windows]
        assert xclock.NAME in names

    def test_attributes(self):
        win, xclock = self.get_win('xclock', '-geometry', '100x200+0+0')
        assert win.wm_name == xclock.NAME
        assert win.wm_class == xclock.NAME + '.XClock'
        assert win.w == 100
        assert win.h == 200
        # measure the width and the height of WM decorations
        ofs_x = win.x
        ofs_y = win.y
        xclock.child.kill()
        win, xclock = self.get_win('xclock', '-geometry', '+30+40')
        assert win.x == 30 + ofs_x
        assert win.y == 40 + ofs_y - 24  # magic number needed for my WM

    def X_test_activate(self):
        ewmh = EWMH()
        orig = ewmh.get_active()
        win, xfontsel = get_win('xfontsel', '-geometry', '+0+0')
        win.activate()
        time.sleep(0.5)
        active = ewmh.get_active()
        assert active.id is not None
        assert active.id == win.id
        orig.activate()
        time.sleep(0.5)
        active = ewmh.get_active()
        assert active.id == orig.id

    def test_resize_and_move(self):
        win, xclock = self.get_win('xclock', '-geometry', '+0+40')
        ofs_x = win.x
        ofs_y = win.y
        win.resize_and_move(10, 20, 30, 40)
        ewmh = EWMH()
        win2 = ewmh.by_title(xclock.NAME)[0]
        assert win.id == win2.id
        assert win2.x == 10 + ofs_x
        assert win2.y == 20 + ofs_y - 36  # top bar in Ubuntu problematic?
        assert win2.w == 30
        assert win2.h == 40

    def test_geometry(self):
        self.check_geometry('100x200+30+40')



# default for tox stub is to Fail
# def test_ewmh():
#     assert False
