import os
import sys
import logging
import elpotrero.lib.files as libfiles
import elpotrero.lib.util as elutil
from loadconfigtools import setup_python_path


def _here():
    """standard "here" helper function"""
    return os.path.dirname(os.path.realpath(__file__))


def main(args):
    """ This is the createdirstruct or Create Directory Structure script

    The purpose of this script is to create the rootpath directory
    the rootpath directory is where the project is found by web services

    There are two things involved in creating the rootpath
    1. Creating the actual folders in rootpath to store and link to
    2. Creating symlinks between files in the project home and rootpath

    Keep in mind that project home is where we keep the installation,
    it's set up in a way that allows me to easily keep track of the files
    """

    global _logger
    formatter = elutil.create_logformatter("%(filename)s %(message)s", "")
    elutil.setup_logging('/tmp/logs', scrnlog=True,
                         logname='scripts.bootstrap.createdirstruct.debug',
                         screen_formatter=formatter,
                         debug=elutil.findflag('--d', args))

    _logger = logging.getLogger('standard.core')

    # add the directory where configurationvalues is found to the sys.path
    setup_python_path()

    import configurationvalues as confvals

    _logger.info("importing configuration values")

    projectpath = confvals.getprojectpath()
    fullrootpath = confvals.getrootpath()
    envrpath = confvals.getenvironmentpath()

    fpath_gunicorn = confvals.getlayoutvalue('gunicornscript')

    _logger.debug("set fullrootpath = {0}".format(fullrootpath))
    _logger.debug("set envrpath = {0}".format(envrpath))
    _logger.debug("set fpathgunicorn = {0}\n".format(fpath_gunicorn))

    _logger.info("making directories in {0}".format(fullrootpath))

    libfiles.mkdir_p(os.path.join(fullrootpath, 'private'))
    libfiles.mkdir_p(os.path.join(fullrootpath, 'backup'))
    libfiles.mkdir_p(os.path.join(fullrootpath, 'logs', 'nginx'))
    libfiles.mkdir_p(os.path.join(fullrootpath, 'logs', 'gunicorn'))
    libfiles.mkdir_p(os.path.join(fullrootpath, 'logs', 'supervisor'))
    libfiles.mkdir_p(os.path.join(fullrootpath, 'scripts'))
    libfiles.mkdir_p(os.path.join(fullrootpath, 'public', 'media', 'dynamic'))
    libfiles.mkdir_p(os.path.join(fullrootpath, 'public', 'media', 'static'))

    libfiles.mkdir_p(envrpath)

    libfiles.symcheck(os.path.join(projectpath, 'templates'),
                      os.path.join(fullrootpath, 'private', 'templates'))

    # due to changes in gunicorn the following line was changed from
    # projectpath/project to projectpath.  Gunicorn is looking for
    # projectpath/project.wsgi to execute gunicorn project.wsgi:application
    libfiles.symcheck(projectpath,
                      os.path.join(fullrootpath, 'private', 'djangoproject'))

    libfiles.symcheck(os.path.join(projectpath, fpath_gunicorn),
                      os.path.join(fullrootpath, 'scripts', 'gunicorn.sh'))

    libfiles.symcheck(envrpath,
                      os.path.join(fullrootpath,
                                   'private', 'virtual_environment'))

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
