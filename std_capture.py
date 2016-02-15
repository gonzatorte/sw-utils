import os, sys
# import threading


# t_data = threading.local()
capture_stack = None
capture_manager = None


def configure():
    _capture_stack = []
    _capture_stack.append((sys.__stdout__, sys.__stderr__))
    thismodule = sys.modules[__name__]
    setattr(thismodule, 'capture_stack', _capture_stack)
    _capture_manager = StdCapture()
    setattr(thismodule, 'capture_manager', _capture_manager)
    # t_data.capture_stack = _capture_stack


def desconfigure():
    thismodule = sys.modules[__name__]
    _capture_stack = []
    _capture_stack.append((sys.__stdout__, sys.__stderr__))
    thismodule = sys.modules[__name__]
    setattr(thismodule, 'capture_stack', _capture_stack)
    _capture_manager = StdCapture()
    setattr(thismodule, 'capture_manager', _capture_manager)
    # t_data.capture_stack = _capture_stack

    sys.stdout = sys.__stdout__
    sys.stderr = sys.__stderr__


def get_capture():
    thismodule = sys.modules[__name__]
    return thismodule.capture_manager


def get_capture_mng(out=None, err=None):
    c = get_capture()
    c.curr_out = out
    c.curr_err = err
    return c


def start_capture(out=None, err=None):
    c = get_capture()
    c.curr_out = out
    c.curr_err = err
    c._start_capture()
    return c


def stop_capture():
    c = get_capture()
    c._end_capture()
    return c


class DummyFile(object):
    def write(self, x): pass


class StdCapture:
    def __init__(self):
        self.curr_out = None
        self.curr_err = None

    def _start_capture(self):
        if self.curr_out is None:
            self.curr_out = DummyFile()
        if self.curr_err is None:
            self.curr_err = DummyFile()
        thismodule = sys.modules[__name__]
        thismodule.capture_stack.append((self.curr_out, self.curr_err))
        sys.stdout = self.curr_out;
        sys.stderr = self.curr_err;
        return self

    def _end_capture(self):
        thismodule = sys.modules[__name__]
        thismodule.capture_stack.pop()
        (out, err) = thismodule.capture_stack[-1]
        self.curr_out = out
        self.curr_err = err
        sys.stdout = out
        sys.stderr = err
        return self

    def __enter__(self, *args, **kwargs):
        self._start_capture()

    def __exit__(self, exc_type, exc_val, exc_tb, *args, **kwargs):
        self._end_capture()
