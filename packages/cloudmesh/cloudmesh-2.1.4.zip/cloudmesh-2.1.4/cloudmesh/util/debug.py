import sys
import os


def LINE(back=0):
    return sys._getframe(back + 1).f_lineno


def FILE(back=0):
    return sys._getframe(back + 1).f_code.co_filename


def FUNC(back=0):
    return sys._getframe(back + 1).f_code.co_name


def WHERE(back=0):
    frame = sys._getframe(back + 1)
    return "{0} {1} {2}()".format(os.path.basename(frame.f_code.co_filename),
                                  frame.f_lineno,
                                  frame.f_code.co_name)
