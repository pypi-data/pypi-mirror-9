import os
import shutil
from .. import util
import glob
import subprocess
import platform

from . import base

class Builder(base.Builder):
    def __init__(self, path, version):
        super(Builder,self).__init__(path, version)

    def get_all_files(self, directory, expression=None):
        matches = []
        for root, dirnames, filenames in os.walk(directory, topdown=True):
            dirnames[:] = [d for d in dirnames if d not in self.IGNORE_PATTERNS]
            for filename in filenames:
                matches.append(os.path.join(root, filename))
        return matches


    def build(self,jobs='1',exclude=None):
        self.IGNORE_PATTERNS = ('CVS','.git','.svn')

        self.files['bin'] = self.get_all_files(
                os.path.join(self.path, platform.system())
                )
        return self.files

