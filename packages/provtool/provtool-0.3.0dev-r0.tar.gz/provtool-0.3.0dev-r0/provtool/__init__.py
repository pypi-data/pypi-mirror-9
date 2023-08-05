from __future__ import absolute_import, print_function

import os
import sys
import logging
import plistlib
import fnmatch

DEFAULT_PROVPROF_DIR = os.path.expanduser('~/Library/MobileDevice/Provisioning Profiles')


logger = logging.getLogger("%s[%s]" % (os.path.basename(sys.argv[0]),
                                       os.getpid(), ))


def isProvFile(filePath):
    return filePath.endswith('.mobileprovision')


def plistStringFromProvFile(path):
    beginToken = '<?xml'
    endToken = '</plist>'
    f = open(path)
    data = f.read()
    begin = data.index(beginToken)
    end = data.rindex(endToken) + len(endToken)
    return data[begin:end]


def name(filePath):
    plistString = plistStringFromProvFile(filePath)
    plist = plistlib.readPlistFromString(plistString)
    return plist['Name']


def path(provName, path=DEFAULT_PROVPROF_DIR, patternMatch=False):
    paths = []
    for f in os.listdir(path):
        if isProvFile(f):
            filePath = os.path.join(path, f)
            if not patternMatch and name(filePath) == provName:
                paths.append(filePath)
            elif patternMatch and fnmatch.fnmatch(name(filePath), provName):
                paths.append(filePath)
    return paths


def uuid(path):
    fullpath = os.path.expanduser(path)
    if not isProvFile(fullpath):
        err = '%s is not a Provisioning Profile' % (fullpath)
        #sys.stderr.write(err)
        raise ValueError(err)  # TODO: ValueError the right kind of exception?
        return None
    plistString = plistStringFromProvFile(fullpath)
    plist = plistlib.readPlistFromString(plistString)
    return plist['UUID']


def list(dir=DEFAULT_PROVPROF_DIR):
    l = []
    for f in os.listdir(dir):
        if isProvFile(f):
            l.append("%s : '%s'" % (f, name(os.path.join(dir, f))))
    return l
