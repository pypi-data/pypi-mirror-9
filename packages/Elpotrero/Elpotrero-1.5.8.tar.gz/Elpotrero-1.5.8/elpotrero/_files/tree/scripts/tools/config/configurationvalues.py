import os
import sys
import yaml
import shyaml
import elpotrero.lib.util as elutil

# Note: configuration file for this tool and all other tools in this directory
_TOOLSCONFIG = "tools.config.yaml"


def _here():
    """standard "here" helper function"""
    return os.path.dirname(os.path.realpath(__file__))


def loadyaml(configfile):
    """Helper function to pull up the config file

    returns a yaml dict
    """
    with file(configfile, 'r') as stream:
        return yaml.load(stream)


def _cwdprojectpath():
    # get the project path by splitting off the current working directory at
    # "scripts".  filelayout.yaml never changes it's path, also
    # this tool is always found next to extractconfig.py, so those
    # things can be assumed

    pathlist = os.getcwd().split(os.path.sep)
    index = elutil.lastindex(pathlist, 'scripts')
    return os.path.sep.join(pathlist[:index])


def getformalprojectpath():
    """
    Utility function to create a project path name based on the
    values found in configuration.basic
    """
    projectname = getconfigvalue('project')
    projectdir = getconfigvalue('projdir')
    branchname = getbranch()

    return "{0}/{1}/{2}".format(projectdir, projectname, branchname)


def getprojectpath():
    """
    Utility to get the project path based on WHERE THIS FILE IS LOCATED
    I'm finding the above formal project path method does not do what I want
    because it limits me to using only the  configuration file.

    I'd rather use the location of the installation files as a determiner
    of what the projdir is!
    """
    pathlist = _here().split(os.path.sep)
    index = elutil.lastindex(pathlist, 'scripts')
    return os.path.sep.join(pathlist[:index])


def getrootpath():
    """ Utility function to create a project path name based on the
    values found in configuration.basic
    """
    projectdirname = "{0}.{1}".format(
        getconfigvalue('project'), getconfigvalue('domain'))

    fullrootpath = os.path.join(
        getconfigvalue('rootpath'), projectdirname)

    return fullrootpath


def getenvironmentpath():
    """ Utility function returning the full path of the environment directory
    """
    return os.path.join(getconfigvalue('environment'), "{0}.{1}".format(
        getconfigvalue('project'), getbranch()))


def _cwdfilelayout():
    global _TOOLSCONFIG

    # Note: I have to use the _here method, because if I access this script
    # from another directory, the vm won't know where the TOOLSCONFIG file is
    ptoolsconfig = "{0}/{1}".format(_here(), _TOOLSCONFIG)
    filelayoutpath = loadyaml(ptoolsconfig)['filelayout']

    return os.path.join(_cwdprojectpath(), filelayoutpath)


def _cwdfullpath(confkey):
    """ Helper function to retrieve the configuration paths
        that are defined in the filelayout conf file

        confkey refers to either configuration.branch or configuration.basic
        which should be passed in as "configuration\.branch" or
        "configuration\.basic"

        NOTE: The values retrieved using this function are appended to the
        project directory path.  So you might want to be careful with this,
        since you could ask for a totally unrelated value and get something
        that shouldn't be appended to a project path.
    """
    ydict = loadyaml(_cwdfilelayout())
    configpath = shyaml.mget(ydict, confkey)
    return os.path.join(_cwdprojectpath(), configpath)


def _cwdconfigbasic():
    return _cwdfullpath('configuration\.basic')


def getbranch():
    """ Helper function to retrieve the name of the branch we are working on

        NOTE: There isn't any point in retrieving the config branch file, since
            all I want is the branch value
    """
    # return the branch value found in the yaml conf file configuration.branch
    bpath = _cwdfullpath('configuration\.branch')
    return loadyaml(bpath)['branch']


def getbranchindex():
    """Return the index of the branch key
        """

    branch = getbranch()
    branchlist = getconfigvalue('branch', isbranchdependent=False)

    # make sure the branch value we got is among the available branch values
    # found in configuration.basic.  If so, then return the index
    if branchlist.count(branch) == 0:

        errmsg = "branch = {0}\nbranchlist = {1}".format(branch, branchlist)

        raise ValueError("The branch value from configuration.branch doesn't"
                         " appear in configuration.basic\n."
                         + errmsg)

    return branchlist.index(branch)


def getlayoutvalue(key):
    """ Helper function to get values from the filelayout file
    """
    ydict = loadyaml(_cwdfilelayout())
    return shyaml.mget(ydict, key)


def getconfigvalue(key, isbranchdependent=True):
    """ Helper function to get values from the configuration.basic file
        a lot of the values that I'll request will depend on what branch I
        am using.

        I internally find the relevent branch using the getbranch method
        in this class

    Keyword arguments:
        key -- the key argument used

        NOTE: shyaml.mget drills down to find the key value, for example:
            "tools.config" is assumed to be a value in dictionary form

            tools = { 'config':someval }

            but "tools\.config" would be considered a single keyname of:

            tools.config = someval
    """
    ydict = loadyaml(_cwdconfigbasic())
    value = shyaml.mget(ydict, key)

    # if I don't care about the branch, then just
    # return whatever value I find.
    if not isbranchdependent:
        return value

    errmsg_vals = "\nValues are:\nbranch = {0}\nconfigurationpath = {1}\n" \
        "key requested = {2}\nextracted ymldict = {3}\n".format(
            getbranch(), _cwdconfigbasic(),
            key, ydict)

    if type(value) is list:
        bindex = getbranchindex()

        # check to make sure that the len of the value list isn't less than the
        # branch index we are searching for.
        if len(value) < bindex:
            raise ValueError("The branch index is higher than the length of "
                             "the list value returned by the key you "
                             "requested.\nThis is probably a problem with the "
                             "configuration.basic file.\n"
                             "You should check the key in it.\n" + errmsg_vals)
        # Otherwise, continue to return the value based on the bindex
        return value.pop(bindex)
    else:
        return value


def getconfigkeys():
    """ Helper function to return the keys for the configuration.basic file
    """
    ydict = loadyaml(_cwdconfigbasic())
    return ydict.keys()


def getfilelayoutkeys():
    """ Helper function to return the keys for the filelayout file
    """
    ydict = loadyaml(_cwdfilelayout())
    return ydict.keys()


def getconfigurationcontext():
    """ The purpose of this function is to create a context dictionary
    for use in a template renderer

    if you look at how keys are generated, you'll notice I replace the
    '.' with a '\.'

    e.g.  bind.zones ->  bind\.zones
    """
    context = dict()
    keys = getconfigkeys()

    for k in keys:
        context[k] = getconfigvalue(k)

    return context


def main(args):
    print getconfigurationcontext()


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
