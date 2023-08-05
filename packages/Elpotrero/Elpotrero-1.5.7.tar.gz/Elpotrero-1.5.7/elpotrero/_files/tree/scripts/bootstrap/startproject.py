import os
import sys
import logging
import elpotrero.lib.util as libutil
import elpotrero.lib.files as libfiles
from loadconfigtools import setup_python_path


def main(args):
    """
    Note: The purpose of this script is to create a django project directory
    in the projects main installation directory. e.g:

    home/user/project/... -- this is where the django proj dir goes--


    using django-admin we also customize our own modified version of the
    settings.py file, but we keep both the one that is normally created
    by django-admin, and the custom version in two files

    settings.modd.py - the custom version
    settings.orig.py - the original version django-admin makes
    """
    setup_python_path()
    import configurationvalues as confvals

    global _logger
    formatter = libutil.create_logformatter("%(filename)s %(message)s", "")
    libutil.setup_logging('/tmp/logs', scrnlog=True,
                          logname='scripts.bootstrap.startproject.debug',
                          screen_formatter=formatter,
                          debug=libutil.findflag('--debug', sys.argv))

    _logger = logging.getLogger('standard.core')

    projectname = confvals.getconfigvalue('project')
    projectpath = confvals.getprojectpath()
    projectbranch = confvals.getbranch()

    if not os.path.exists(projectpath):
        print "target directory needs to be created first"
        print "target directory is = {0}".format(projectpath)
        sys.exit(1)

    # Note: this is usually located in scripts/conf/django/_build
    # Check filelayout.conf to find the path to where we install the custom
    # generated settings.py
    pdjango = confvals.getlayoutvalue('build.paths.django')
    src_settings = os.path.join(projectpath, pdjango, '_build')
    _logger.debug("pdjango = {0}".format(pdjango))
    _logger.debug("projectpath = {0}".format(projectpath))
    _logger.debug("src_settings = {0}".format(src_settings))

    dtmp = os.path.join(os.getcwd(), 'tmp')
    if not os.path.exists(dtmp):
        os.makedirs(dtmp)
    os.chdir(dtmp)

    commanddict = dict()
    commanddict['admin'] = ['django-admin.py', 'startproject',  projectname]
    libutil.execcommand(commanddict, 'admin', 'django-admin')

    # sourcedir is where the files created by django-admin are located
    sourcedir = os.path.join(dtmp, projectname)

    # Check if manage.py is in /projectpath/manage.py
    #
    # Note: manage.py has to be one directory above
    #   /home/projectpath/project/settings.py
    #
    if not os.path.exists(os.path.join(projectpath, 'manage.py')):
        libfiles.copyanything(os.path.join(sourcedir, 'manage.py'),
                              os.path.join(projectpath, 'manage.py'))

    if not os.path.exists(os.path.join(projectpath, projectname)):
        libfiles.copyanything(os.path.join(sourcedir, projectname),
                              os.path.join(projectpath, projectname))

        dst_settings = os.path.join(projectpath, projectname, '_settings')
        if not os.path.exists(dst_settings):
            os.makedirs(dst_settings)

        # copy over the settings.py file made by django-admin to settings.orig
        libfiles.copyanything(
            os.path.join(sourcedir, projectname, 'settings.py'),
            os.path.join(dst_settings, 'settings.py.orig'))

        # get rid of the old settings.py
        # Note: this is not located in projectpath/project/_settings
        # it's located in projectpath/project
        os.remove(os.path.join(projectpath, projectname, 'settings.py'))

        # copy over our version of settings.py and link it to settings.modd
        libfiles.copyanything(
            os.path.join(src_settings, 'settings.py'),
            os.path.join(dst_settings, 'settings.py.modd'))

        libfiles.copyanything(
            os.path.join(src_settings, 'settings_main.py'),
            os.path.join(dst_settings, 'settings_main.py'))

        localsettings = "local_{0}.py".format(projectbranch)
        libfiles.copyanything(
            os.path.join(src_settings, 'settings_local.py'),
            os.path.join(dst_settings, localsettings))

        # now make a symlink between settings.modd and settings.py
        #  so that now the custom settings file is what will be used
        # we are linking projectpath/project/_settings/settings.py.modd
        # to projectpath/project/settings.py
        libfiles.symcheck(
            os.path.join(dst_settings, 'settings.py.modd'),
            os.path.join(projectpath, projectname, 'settings.py'))

        libfiles.symcheck(
            os.path.join(dst_settings, localsettings),
            os.path.join(projectpath, projectname, 'settings_local.py'))

        # Note: we keep a copy of the original and the mod so I can compare
        # and contrast between the two

    libfiles.removedirectory(dtmp)

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
