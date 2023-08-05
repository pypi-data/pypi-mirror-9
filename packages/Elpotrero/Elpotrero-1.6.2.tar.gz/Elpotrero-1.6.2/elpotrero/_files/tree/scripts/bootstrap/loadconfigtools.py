#!/usr/bin/env python
import os
import sys
import yaml
import elpotrero.lib.util as elutil


def getprojectpath():
    """ Helper function to find the project path"""

    pathlist = os.getcwd().split(os.path.sep)
    index = elutil.lastindex(pathlist, 'scripts')
    return os.path.sep.join(pathlist[:index])


# this function has to be set up before it's called
def setup_python_path():
    """ This function appends to the python path the directory where the
        configuration tool is"""

    with file("./meta.yaml", 'r') as stream:
        filelayout = yaml.load(stream)['filelayout']

    with file(os.path.join(getprojectpath(), filelayout), 'r') as stream:
        configdir = yaml.load(stream)['libpath.tools.config']

    sys.path.append(os.path.join(getprojectpath(), configdir))

setup_python_path()
import configurationvalues as confvals


def getconftool():
    value = confvals.getlayoutvalue('tools.config')
    return os.path.join(getprojectpath(), value)


def getbranchtool():
    value = confvals.getlayoutvalue('tools.branch')
    return os.path.join(getprojectpath(), value)


def getgeneratetool():
    value = confvals.getlayoutvalue('tools.generate')
    return os.path.join(getprojectpath(), value)


def main(args):
    keyarg = elutil.findarg("-k", args)

    if keyarg == "conftool":
        print getconftool()
    elif keyarg == "branchtool":
        print getbranchtool()
    elif keyarg == "generatetool":
        print getgeneratetool()


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
