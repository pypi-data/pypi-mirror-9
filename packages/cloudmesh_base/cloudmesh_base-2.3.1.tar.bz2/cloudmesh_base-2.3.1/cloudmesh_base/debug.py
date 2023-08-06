import os
import sys


def LINE(back=0):
    """
    Prints the line number where this method is called from.
    
    :param back: the context of the call, typically you can omit
    """
    return sys._getframe(back + 1).f_lineno


def FILE(back=0):
    """
    Prints the filename where this method is called from.
    
    :param back:
    """
    return sys._getframe(back + 1).f_code.co_filename


def FUNC(back=0):
    """
    Prints the function name where this method is called.
    
    :param back: the context of the call, typically you can omit
    """
    return sys._getframe(back + 1).f_code.co_name


def WHERE(back=0):
    """
    Prints information about where this function is called, including filename and line number as well as function.
    
    :param back: the context of the call, typically you can omit
    """
    frame = sys._getframe(back + 1)
    return "{0} {1} {2}()".format(os.path.basename(frame.f_code.co_filename),
                                  frame.f_lineno,
                                  frame.f_code.co_name)
