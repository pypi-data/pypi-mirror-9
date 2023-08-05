import os
import yaml
import shutil


def _here():
    """standard "here" helper function"""
    return os.path.dirname(os.path.realpath(__file__))


def _cwd():
    return os.getcwd()


class DjangoInstall:

    # meta refers to the configuration file for this script
    meta = "_files/conf.yaml"

    # the basic conf is basic for the installation we are
    # setting up.
    basicconfig = None
    destinationfolder = None

    def __init__(self, basicconfigfile=None, destinationfolder=""):

        if basicconfigfile is None:
            meta = self._getmetainfo()
            self.basicconfig = os.path.join(_here(),
                                            meta['filepaths']['basic']['src'])
        else:
            self.basicconfig = os.path.join(_cwd(), basicconfigfile)

        self.destinationfolder = destinationfolder

    def _getbranches(self):
        """ util function to quickly get back the branches we will be using"""
        if not self.basicconfig:
            conf = self._getmetainfo()
            self.basicconfig = os.path.join(_here(), conf['basic']['src'])

        stream = open(self.basicconfig)
        return yaml.load(stream)['branch']

    def _getmetainfo(self):
        """ function that returns a dict with all the config info
        """
        stream = open(os.path.join(_here(), self.meta))
        return yaml.load(stream)

    def install(self):
        conf = self._getmetainfo()

        # copy the main tree
        shutil.copytree(
            os.path.join(_here(), conf['directorystructure']['src']),
            os.path.join(_cwd(), self.destinationfolder))

        dstbasic = os.path.join(_cwd(), self.destinationfolder,
                                conf['filepaths']['basic']['dst'])

        shutil.copyfile(self.basicconfig, dstbasic)

        branches = self._getbranches()
        for b in branches:
            src = os.path.join(_here(), conf['filepaths']['virtualenv']['src'])

            filename = src.split(os.path.sep)[-1].replace('BRANCH', b)

            dst = os.path.join(_cwd(), self.destinationfolder,
                               conf['filepaths']['virtualenv']['dst'],
                               filename)

            shutil.copyfile(src, dst)
