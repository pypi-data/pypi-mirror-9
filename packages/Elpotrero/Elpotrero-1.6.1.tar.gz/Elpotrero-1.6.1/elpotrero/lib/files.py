import inspect, os, errno, shutil, yaml, re
import elpotrero.lib.util as libutil

def symcheck(src, dst):
    """checks to see if the sym link exists, if not, creates the link"""
    if not os.path.lexists(dst):
        os.symlink(src, dst)
    
def mkdir_p(path):
    """duplicates functionality of bash "make -p" command"""
    try:
        os.makedirs(path)
    except OSError as exc:
        if exc.errno == errno.EEXIST:
            pass
        else: raise


def hereis():
    print os.getcwd()


def load_yaml(src):
    stream = open(src, 'r')
    extract = yaml.load(stream)
    stream.close()
    return extract 

def copyanything(src, dst):
    """
        copies everything in a directory tree, or copies a file 
            see http://stackoverflow.com/questions/1994488/copy-file-or-directory-in-python
    """
    try:
        shutil.copytree(src, dst)
    except OSError as exc: # python >2.5
        if exc.errno == errno.ENOTDIR:
            shutil.copy(src, dst)
        else: raise


def removedirectory(directoryname):
    directorypath = os.path.join(os.getcwd(), directoryname)
    return removedirectory_abs(directorypath, directoryname)


def removedirectory_abs(directorypath, directoryname=""):

    if os.path.exists(directorypath):
        # check if it is a directory
        if os.path.isdir(directorypath):
            isremove = libutil.confirmation("Found a {0} directory already in place. Remove it [Y/n]?".format(directoryname))
            if isremove:
                shutil.rmtree(directorypath)
            else:
                libutil.exit_err("Cannot install over existing directory.")

        elif os.path.isfile(directorypath):
            isremove = libutil.confirmation("while trying to remove previous instance of {0}, came across a file that has that name in the current working directory.  Would you like to remove it anyway [Y/n]? ".format(directoryname))
            if isremove:
                os.unlink(directorypath)
            else:
                libutil.exit_err("Cannot install over existing file (where the {0} directory is supposed to go).".format(directoryname))

        else:
            libutil.exit_err("Exiting with error - trying to remove previous instance of {0} directory, and found something that is not registering as either a file or a directory.".format(directoryname))
    


def expand_pathlist(directorylist, expansionterms, expandkey):
    """creates the script directories

        directorylist - a list of directory paths
        expansionterms - a list of expansion terms
        expandkey - the keyword to check for in the directorylist items

        return an expanded list based on the terms given in expansionterms
    
    """
    expansionlist = list()
    
    for pathstr in directorylist: 
        # check to see if the expandkey is located within the path string
        # if it is than break the pathstring apart and find the full word
        # used inside the string and then search for that word among the listed
        # items of the path.
        if pathstr.find(expandkey) != -1:
            plist = pathstr.split('/')
            plistkey = libutil.regxListFind(plist, expandkey)
            plist_index = plist.index(plistkey)
            prog = re.compile(expandkey)

            for expandterm in expansionterms:
                sub = prog.sub(expandterm, plistkey) 
                plist[plist_index] = sub 

                # make sure to rejoin the pathlist with a "/"
                expansionlist.append("/".join(plist))
        else:
            # no need to rejoin anything since we never broke it down
            expansionlist.append(pathstr)

    return expansionlist

