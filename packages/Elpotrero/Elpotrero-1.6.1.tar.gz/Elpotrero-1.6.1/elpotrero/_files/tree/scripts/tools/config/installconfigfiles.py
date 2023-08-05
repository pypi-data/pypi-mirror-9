import os
import sys
import re
import logging
import elpotrero.lib.files as libfiles
import elpotrero.lib.util as elutil
import configurationvalues as confvals


_logger = None


def getconfigurationpath(filelayoutkey, filename):
    """ Util to get the full path of conf file"""

    pathfile = os.path.join(
        confvals.getprojectpath(),
        confvals.getlayoutvalue(filelayoutkey),
        '_build',
        filename)

    _checkpathexists(pathfile)

    return pathfile


def _getpath(pathkey):
    """ Another simple util to cut down on all the code.

    All it does is pull out the configvalue based on the path key and does
    some error checking to make sure the path exists.
    """
    global _logger

    pathfile = confvals.getconfigvalue(pathkey)

    _logger.debug("key = {0}, path = {1}".format(pathkey, pathfile))

    _checkpathexists(pathfile)

    return pathfile


def _checkpathexists(pathfile):
    """ This util is just a helper that checks if the path/file exists.  If
    it does not, then exit and give a message
    """
    global _logger

    ipsrcfile = os.path.exists(pathfile)

    _logger.debug("{0} exist - {1}".format(pathfile, ipsrcfile))

    if not ipsrcfile:
        _logger.info("exiting because {0} does not exist".format(pathfile))
        sys.exit(1)


def getdestinations():
    # these are all the paths to the files we intend to modify
    # all the configuration options are located in basic_configuration.conf
    pdst = dict()
    pdst['bindnamed'] = _getpath('paths.bind.named')
    pdst['bindzones'] = _getpath('paths.bind.zones')
    pdst['nginxavail'] = _getpath('paths.nginx.available')
    pdst['nginxenabl'] = _getpath('paths.nginx.enabled')
    pdst['supervisor'] = _getpath('paths.supervisor\.conf')

    project = confvals.getconfigvalue('project')
    projectpath = confvals.getprojectpath()
    pdst['django'] = "{0}/{1}".format(projectpath, project)

    return pdst


def getsources():
    """ path to the conf versions we have that are meant to be installed
     these files are all installed in scripts/conf/ name of conf / _build
     we're going to use this file name a few times
     """

    global _logger

    confname = getconfnames()

    psrc = dict()
    psrc['bindnamed'] = getconfigurationpath('build.paths.bind',
                                             'named.conf.local')

    psrc['bindzones'] = getconfigurationpath('build.paths.bind',
                                             confname['bind'])

    psrc['nginxavail'] = getconfigurationpath('build.paths.nginx',
                                              confname['nginx'])

    psrc['supervisor'] = getconfigurationpath('build.paths.supervisor',
                                              confname['supervisor'])

    _logger.debug("psrc['bindnamed'] = {0}".format(psrc['bindnamed']))
    _logger.debug("psrc['bindzones'] = {0}".format(psrc['bindzones']))
    _logger.debug("psrc['nginxavail'] = {0}".format(psrc['nginxavail']))
    _logger.debug("psrc['supervisor'] = {0}".format(psrc['supervisor']))

    return psrc


def getconfnames():
    """
    returns a dictionary of the correct names of the configuration files
    we are using this does NOT return full path names!
    """
    project = confvals.getconfigvalue('project')
    domain = confvals.getconfigvalue('domain')

    confnames = dict()
    confnames['bind'] = 'db.{0}.{1}'.format(project, domain)
    confnames['nginx'] = '{0}.{1}'.format(project, domain)
    confnames['supervisor'] = '{0}.conf'.format(project)

    return confnames


def installconfigurationfiles(dests, source):
    """
    Contains all the code to install the configuration files found in
    scripts/conf to /etc/bind, /etc/nginx, etc.

    Keyword Argumetns

    dests - destination paths to where we intend to copy and modify
                configuration files

    source - source paths to the configuration files we have in the
                scripts/conf directory
    """
    # bind installation
    # bindnamed is contents of the file found in /etc/bind/named.conf
    # bindconf is the addition we wish to make to /etc/bind/named.conf
    fbind = open(dests['bindnamed'], 'r')
    bindnamed = fbind.read()
    fbind.close()

    fbind = open(source['bindnamed'], 'r')
    bindconf = fbind.read()
    fbind.close()

    # if the addition is not already there, then add it and write it
    m = re.search(bindconf, bindnamed)
    if m is None:
        fbind = open(dests['bindnamed'], 'w')
        fbind.write("{0}\n{1}".format(bindnamed, bindconf))

    # now copy the zone file we have for this project
    # to the /etc/bind/zones directory
    libfiles.copyanything(source['bindzones'],
                          dests['bindzones'])

    # nginx installation
    #   first place our nginx conf file into /etc/nginx/sites-available
    #   then symlink it to nginx/sites-enabled
    libfiles.copyanything(source['nginxavail'],
                          dests['nginxavail'])

    confname = getconfnames()
    src = os.path.join(dests['nginxavail'], confname['nginx'])
    dst = os.path.join(dests['nginxenabl'], confname['nginx'])

    libfiles.symcheck(src, dst)

    # supervisor installation
    libfiles.copyanything(source['supervisor'],
                          dests['supervisor'])


def uninstallconfigurationfiles(targetpaths, sources):
    """
    Contains all the code to delete installed configuration files found in
    /etc/bind, /etc/nginx, etc.

    Keyword Argumetns

    dests - destination paths to where we installed the configuration files
        that are meant to be deleted

    source - source paths to the configuration files we have in the
                scripts/conf directory

    """
    # bind un-installation

    # we have to check /etc/bind/named.conf.local for anything we put
    # in there and delete it
    fbind = open(targetpaths['bindnamed'], 'r')
    bindtarget = fbind.read()
    fbind.close()

    fbind = open(sources['bindnamed'], 'r')
    bindconf = fbind.read()
    fbind.close()

    # if the addition to named.conf.local there, then
    #   delete it and rewrite the file
    m = re.search(bindconf, bindtarget)
    if m:
        bindtarget = re.sub(bindconf, "", bindtarget)
        fbind = open(targetpaths['bindnamed'], 'w')
        fbind.write(bindtarget)

    confname = getconfnames()

    # remove the zone file from /etc/bind/zones
    dst = os.path.join(targetpaths['bindzones'], confname['bind'])
    if os.path.exists(dst):
        os.remove(dst)

    # nginx uninstall

    # remove the file from /etc/nginx/sites-available
    available = os.path.join(targetpaths['nginxavail'], confname['nginx'])
    if os.path.exists(available):
        os.remove(available)

    # remove the symlink from /etc/nginx/sites-enabled
    enabled = os.path.join(targetpaths['nginxenabl'], confname['nginx'])
    if os.path.exists(enabled):
        os.remove(enabled)

    # remove conf file from /etc/supervisor/conf.d
    supervisor = os.path.join(targetpaths['supervisor'],
                              confname['supervisor'])

    if os.path.exists(supervisor):
        os.remove(supervisor)


def help():
    return """
This script is used to install configuration files from scripts/conf directory
to various locations in /etc.
Such as /etc/bind/zones /etc/nginx/sites-available, ...

There are two basic modes, install and uninstall

Note that the script will exit during an install if it sees that the required
directories for installation do not exist.  However, it doesn't do a check on
the script/conf files

Usage: sudo $VIRTUAL_ENV/bin/python confinstall.py [FLAG]

flags:
    -h, --help          this help file

    -d, --debug         turn debug logging information on

    -i, --install       run the installation script

    -u, --uninstall     run the uninstallation script

    -is, --installsettings  install settings files as settings.modd
    """


def main(args):
    global _logger
    formatter = elutil.create_logformatter("%(filename)s %(message)s", "")
    elutil.setup_logging('/tmp/logs', scrnlog=True,
                         logname='scripts.bootstrap.installconfs.debug',
                         screen_formatter=formatter,
                         debug=elutil.findflags('-d', '--debug', args))

    _logger = logging.getLogger('standard.core')

    destinationpaths = getdestinations()
    sourcepaths = getsources()

    if elutil.findflags('-h', '--help', args):
        print help()
        sys.exit(0)

    if elutil.findflags('-i', '--install', args):
        installconfigurationfiles(destinationpaths, sourcepaths)
        sys.exit(0)

    if elutil.findflags('-u', '--uninstall', args):
        uninstallconfigurationfiles(destinationpaths, sourcepaths)
        sys.exit(0)

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
