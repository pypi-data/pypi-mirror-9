import os
import sys
import re
import logging
import subprocess
import string
from random import choice
from logging.handlers import RotatingFileHandler


def execcommand(commanddict, commandkey, commandname):
    """executes a command line process and returns info

        commanddict - dictionary containing tuples (commandname,
            parameterstring)

            (commandname should give the full path)

        e.g.
            commandkeydict['start'] = ('ls', '-x')
            commandkeydict['stop'] = ('ls', '-hla')

        commandkey, commandkeykey
    """

    info = dict()
    info['retval'] = subprocess.check_call(commanddict[commandkey])
    if info['retval'] == 0:
        info['message'] = "successfully executed {0} on {1}".format(
            commandkey, commandname)
    else:
        info['message'] = "error executing {0} on {1}".format(
            commandkey, commandname)

    return info


def makepassword(length=8):
    chars = string.letters + string.digits
    return ''.join([choice(chars) for i in range(length)])


def makesecretkey(length=50):
    return "".join([choice(
        "abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)")
        for i in range(50)])


def filterPick(_list, filter):
    # TODO:
    #   move this to a different file

    """
    Searches through a list for a regex term.  Use this instead of list.index
    when the search term is contained WITHIN the list items, for example,
    you are looking for the word "BRANCH" and the item that contains it
    has the word "BRANCH.sh".

    list.index won't return that!

    It returns the full text contained within the list item, so you can
    do a search on that (full text? NOTE: this is why comments are important!)

    original location:
        http://stackoverflow.com/questions/2436607/
        how-to-use-re-match-objects-in-a-list-comprehension

    filter - needs to be a regex.  For example:
        filter = re.compile('(searchterm)').search
    list - the list to search through
    """

    return [item for item in _list for match in (filter(item),) if match]


def regxListFind(_list, find):
    # TODO:
    #   move this to a different file

    regFilter = re.compile('({0})'.format(find)).search
    slist = filterPick(_list, regFilter)

    searchterm = slist[0]

    return searchterm


def create_logformatter(logformat=None, dateformat=None):
    """Helper class to create a standard logging formatter"""

    _lgfrmt = "%(asctime)s - %(levelname)-8s [%(filename)s::%(funcName)s "\
        "%(lineno)d] :: %(message)s\n"
    _dtfrmt = "%Y-%d-%m %H:%M"

    # Note: I get weird errors when I try to make _lgfrmt, and _dtfrmt into
    # default values for logformat and dateformat
    if logformat is None:
        logformat = _lgfrmt

    if dateformat is None:
        dateformat = _dtfrmt

    return logging.Formatter(logformat, dateformat)


def setup_logging(logdir=None, scrnlog=True,
                  txtlog=True, logger_name='standard',
                  logname='Standard.log', loglevel=logging.DEBUG,
                  screen_formatter=None, log_formatter=None, debug=True):
    """
    I forgot where I got this from.  But it's a convenient helper to
    set up logging across files.

    To use, do something like this in the initial file:

        utils_config.setup_logging('/tmp/logs', scrnlog=True,
            logname=_configuration['log.debug'])

        _logger1 = logging.getLogger('standard.core')


    Then when you want to use it somewhere else:
        _logger2 = logging.getLogger('standard.core')

    Both loggers will log to the same place as was set up.  You can also
    change the "loggername" to say 'frank', then the same retrieval
    commands would be:

        _anothernamefor_logger1 = logging.getLogger('frank.core')
        somerandom_logger2 = logging.getLogger('frank.core')
    """

    if debug is True:
        loglevel = logging.DEBUG
    else:
        loglevel = logging.INFO

    logdir = os.path.abspath(logdir)

    if not os.path.exists(logdir):
        os.mkdir(logdir)

    if log_formatter is None:
        log_formatter = create_logformatter()

    log = logging.getLogger(logger_name)
    log.setLevel(loglevel)

    if txtlog:
        txt_handler = RotatingFileHandler(
            os.path.join(logdir, logname), backupCount=5)

        txt_handler.doRollover()
        txt_handler.setFormatter(log_formatter)
        log.addHandler(txt_handler)
        log.info("Logger initialised.")

    if scrnlog:
        if screen_formatter is None:
            screen_formatter = log_formatter

        console_handler = logging.StreamHandler()
        console_handler.setFormatter(screen_formatter)
        log.addHandler(console_handler)


def duplicateList(_list):
    _list2 = list()
    for key in _list:
        _list2.append(list[key])
    return _list2


def confirmation(msg):
    """ Asks the user to input if he wishes to confirm whatever the
    message asks of the user.  Will repeat until it gets a good answer.
    """

    condition = True
    while condition:
        var = raw_input(msg)
        if var == "":
            var = 'Y'

        condition = var.upper() != 'Y' and var.upper() != 'N'
        if condition:
            print "You must enter either 'Y' or 'N'.\n"

        else:
            if var.upper() == 'Y':
                return True
            else:
                return False


def inspect_param(argv, argument, flag=False):
    """retrieve the argument we are looking for.  If flag is set to
        True then just check to see if the argument is there, and don't
        worry if there is an attendent value
    """

    if not flag:
        count = argv.count(argument)
        if count > 0:
            index = argv.index(argument)

            if index + 1 <= len(argv) - 1:
                return argv[index + 1]

        # no success
        return None

    else:
        count = argv.count(argument)
        if count > 0:
            return True
        else:
            return False


def inspect_parameters(argv, s_arg, l_arg, flag=False):
    """retrieve the argument we are looking for.  If flag is set to
        True then just check to see if the argument is there, and don't
        worry if there is an attendent value
    """

    val = inspect_param(argv, s_arg, flag)

    if val is None or val is False:
        val = inspect_param(argv, l_arg, flag)

    return val


def exit_err(err_msg, err_code=1, logger=None):
    """ Helper function to write messages to both the log and the
    console, also gives the error code.
    """
    message = err_msg + "\nExit code {0}\n".format(err_code)

    if logger is None:
        logging.debug(message)
    else:
        logger.debug(message)

    sys.stderr.write("\n" + message + "\n")
    sys.exit(err_code)


def extract_tuplelist(tuplist, key):
    """ This helper function is used with elpotrero.lib.utils.config.tree

        tuplelist - list of tuple values with the structure of (key,value)
        key - the value types you are looking for

        return a list consisting only of the values referenced by key
    """
    somelist = list()

    for item in tuplist:
        if item[0] == key:
            somelist.append(item[1])

    return somelist


def tree(node, parents=None):
    """ Walks through a dictionary/list tree where the format is:
    {'top':{'level1':['item1', 'item2'],
    'level2':{'sublevel1':['item1','item2'], 'sublevel2':""}}}

    and returns a list of items in the format of:
        (directory, top/level1)
        (file, top/level1/item1)
        (file, top/level1/item2)
        (directory, top/level2/sublevel1)
        (file, top/level2/sublevel1/item1)
        (file, top/level2/sublevel1/item1)
        (directory, top/level2/sublevel2)

    node - top level node
    parents - technically the upper directory.  Meant to be a tuple.
    """
    _logger = logging.getLogger('standard.core')

    _logger.debug("node - {0}".format(node))
    if isinstance(node, dict):

        keys = node.keys()

        if parents is None:
            parents = tuple()

        _logger.debug("keys - {0}".format(keys))

        nodelist = list()
        for k in keys:
            _logger.debug("----beg for loop for k in keys----")
            _logger.debug("k - {0}".format(k))
            parentslist = list(parents)
            parentslist.append(k)
            parentstuple = tuple(parentslist)
            _logger.debug("parentslist - {0}".format(parentslist))

            keylist = tree(node[k], parentstuple)

            _logger.debug("keylist - {0}".format(keylist))
            _logger.debug("parents - {0}".format(parents))

            if node[k] is None or not isinstance(node[k], dict):

                _logger.debug(
                    "if node[k] == NONE or not isinstance(node[k], dict)"
                    "\n\tnode - {0}\n\tk - {1}\n\tparents - {2}".format(
                        node, k, parents))

                _logger.debug("len(parents) - ".format(len(parents)))
                path = "/".join(parents)

                if len(parents) == 0:
                    _logger.debug("True!")
                    path = ""
                if len(parents) == 0:
                    keylist.insert(0, ("directory", "{0}".format(k)))
                else:
                    keylist.insert(0, ("directory", "{0}/{1}".format(path, k)))

            nodelist.extend(keylist)
            _logger.debug("----end for loop for k in keys----")
        return nodelist


#def findarg(argkey):
#    """Searches command line input for a key
#    occurence and the value associated with that key
#
#    Keyword argumetns:
#        argkey -- the key flag we are looking for
#        """
#    if sys.argv.count(argkey) > 0:
#        index_key = sys.argv.index(argkey)
#        if index_key + 2 <= len(sys.argv):
#            return sys.argv[index_key + 1]
#
#    elif isinstance(node, list):
#        listval = list()
#        for l in node:
#            path = "/".join(parents)
#
#            listval.append(("file","{0}/{1}".format(path, l)))
#        return listval
#
#    # when the configuration file has a line like
#    # scripts:
#    #   tools:
#    # and nothing afterwards (it's an empty directory), then the recursive
#    # function will go into scripts['tools'] to get a "None" value.  So if
#    # you see that "node" is equal to "None" it means you need to return an
#    # empty list() (DO NOT return a list with the current directory structure)
#    # because we automatically do that when we hit file.  In the case of file,
#    # we also create a list, only we fill it and return that.  Same thing
#    # here only we're not bothering to fill the list (the program thinks there
#    # should be a file there in that case, and it automatically adds in the
#    # directory for that file.  oh just figure it out, OK?
#    elif node == None:
#        return list()


def findarg(argkey, argv):
    """Searches command line input for a key
    occurence and the value associated with that key

    Keyword argumetns:
        argkey -- the key flag we are looking for
        argv -- the list with command line inputs
        """
    if argv.count(argkey) > 0:
        index_key = argv.index(argkey)
        if index_key + 2 <= len(argv):
            return argv[index_key + 1]


def findargs(key1, key2, args):
    """ Same as findarg above, only this one searches for two possible keys
    Keyword argumetns:
        key1 -- first possible key arg we are looking for
        key2 -- second possible key arg we are looking for
        argv -- the list with command line inputs
    """
    val = findarg(key1, args)
    if not val:
        val = findarg(key2, args)

    return val


def findflag(flag, argv):
    """Check command line arguments for a flag argument

    Keyword argumetns:
        flag -- the str representing the flag, e.g. '-f'
        argv -- the list with command line inputs
        """
    if argv.count(flag) > 0:
        return True

    return False


def findflags(flag1, flag2, args):
    """ Same as findflag above, only this one searches for two possible
    flag keys

    Keyword argumetns:
        flag1 -- first possible key arg we are looking for
        flag2 -- second possible key arg we are looking for
        argv -- the list with command line inputs
    """
    val = findflag(flag1, args)
    if not val:
        val = findflag(flag2, args)

    return val


def lastindex(lst, item):
    """
    This helper function solves the problem of finding the last occurence of
    the specified item in a list

    taken from:
        http://stackoverflow.com/questions/6890170/ \
            python-how-to-find-last-occurrence-in-a-list-in-python

    Keywrod arguments:
        lst -- the list being searched
        item -- the item we are looking for
    """
    from itertools import dropwhile

    try:
        return dropwhile(lambda x: lst[x] != item,
                         reversed(xrange(len(lst)))).next()
    except StopIteration:
        raise ValueError("rindex(lst, item): item not in list")
