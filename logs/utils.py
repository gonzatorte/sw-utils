import traceback
import sys


def pre_log(*args, **kargs):
    t, v, tb = sys.exc_info()
    print ">>>>PRE LOG>>>>"
    print '<', args, kargs, t, v, traceback.format_tb(tb, 10), '>'
    print '<', traceback.extract_stack(tb.tb_frame, 10), '>'
    print "<<<<PRE LOG<<<<"
