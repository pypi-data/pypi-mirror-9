import os
from string import Template
import inspect


def grep(pattern, filename):
    """Very simple grep that returns the first matching line in a file.
    String matching only, does not do REs as currently implemented.
    """
    try:
        return (L for L in open(filename) if L.find(pattern) >= 0).next()
    except StopIteration:
        return ''

def path_expand(text):
    """ returns a string with expanded variable.

    :param text: the path to be expanded, which can include ~ and $ variables
    :param text: string

    """
    template = Template(text)
    result = template.substitute(os.environ)
    result = os.path.expanduser(result)
    return result


def yn_choice(message, default='y', tries=None):
    """asks for a yes/no question.
    :param message: the message containing the question
    :param default: the default answer
    """
    # http://stackoverflow.com/questions/3041986/python-command-line-yes-no-input"""
    choices = 'Y/n' if default.lower() in ('y', 'yes') else 'y/N'
    if tries == None:
        choice = raw_input("%s (%s) " % (message, choices))
        values = ('y', 'yes', '') if default == 'y' else ('y', 'yes')
        return True if choice.strip().lower() in values else False
    else:
        while tries > 0:
            choice = raw_input("%s (%s) (%s)" %
                               (message, choices, "'q' to discard"))
            choice = choice.strip().lower()
            if choice in ['y', 'yes']:
                return True
            elif choice in ['n', 'no', 'q']:
                return False
            else:
                print "Invalid input..."
                tries = tries - 1

def banner(txt=None, c="#", debug=True):
    """prints a banner of the form with a frame of # arround the txt::

      ############################
      # txt
      ############################

    .

    :param txt: a text message to be printed
    :type txt: string
    :param c: thecharacter used instead of c
    :type c: character
    """
    if debug:
        print
        print "#", 70 * c
        if txt is not None:
            print "#", txt
            print "#", 70 * c


def HEADING(txt=None):
    """
    Prints a message to stdout with #### surrounding it. This is useful for
    nosetests to better distinguish them.

    :param txt: a text message to be printed
    :type txt: string
    """
    if txt is None:
        txt = inspect.getouterframes(inspect.currentframe())[1][3]

    banner(txt)


def backup_name(filename):
    """
    :param filename: given a filename creates a backup name of the form
                     filename.bak.1. If the filename already exists
                     the number will be increased as  much as needed so
                     the file does not exist in the given location.
                     The filename can consists a path and is expanded
                     with ~ and environment variables.
    :type filename: string
    :rtype: string
    """
    location = path_expand(filename)
    n = 0
    found = True
    while found:
        n = n + 1
        backup = "{0}.bak.{1}".format(location, n)
        found = os.path.isfile(backup)
    return backup
