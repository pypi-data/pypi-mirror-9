# -*- coding: utf-8 -*-
import codecs
import re
from pyhammer.tasks.taskbase import TaskBase
from pyhammer.utils import execProg


class SvnCreateTagTask(TaskBase):
    __dirTrunk = ""
    __dirTag = ""
    __versionFile = ""

    def __init__(self, dirTrunk, dirTag, versionFile=None, includeRevision=False, versionNumber=None, encoding=None):
        super(SvnCreateTagTask, self).__init__()

        self.__dirTrunk = dirTrunk
        self.__dirTag = dirTag
        self.__versionFile = versionFile
        self.__encoding = encoding
        self.__includeRevision = includeRevision
        self.__versionNumber = versionNumber

    def do(self):
        versionNumber = ''
        if self.__versionFile is not None:
            f = None
            content = None
            try:
                if not self.__encoding is None:
                    f = codecs.open(self.__versionFile, 'r', encoding=self.__encoding)
                else:
                    f = open(self.__versionFile, 'r')

                content = f.read()

            except IOError as e:
                self.reporter.failure("Can not read file: %s\nException: %s" % self.__versionFile, e.message)
                return False
            finally:
                if f is not None:
                    f.close()

            version = None
            versionNumber = None
            if self.__includeRevision:
                version = re.search('(\d+)\.(\d+)\.(\d+)\.(\d+)', content)
                versionNumber = version.group(1) + '.' + version.group(2) + '.' + version.group(3) + '.' + version.group(4)
            else:
                version = re.search('(\d+)\.(\d+)\.(\d+)', content)
                versionNumber = version.group(1) + '.' + version.group(2) + '.' + version.group(3)
        elif self.__versionNumber is not None:
            versionNumber = self.__versionNumber
        else:
            self.reporter.failure("Version file or Versio Number is None, please give a path to search version.")
            return False

        self.__dirTag = self.__dirTag + '/' + versionNumber

        self.reporter.message("TRUNK DIR: %s" % self.__dirTrunk)
        self.reporter.message("TAG DIR: %s" % self.__dirTag)
        commitMessage = "Created by Build"
        command = 'svn copy --non-interactive --trust-server-cert "' + self.__dirTrunk + '" "' + self.__dirTag + '" -m \"' + commitMessage + '\"'

        self.reporter.message("COMMAND: %s" % command)

        return execProg(command, self.reporter) == 0