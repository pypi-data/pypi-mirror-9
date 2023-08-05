# -*- coding: utf-8 -*-
from pyhammer.filters.filefilter import FileFilter


class MsTestFileFilter(FileFilter):
    def __init__(self, mode='Release', exclude=[]):
        if mode is None:
            mode = 'Release'
        FileFilter.__init__(self, include=['*Tests.dll'], folderPattern='*\\bin\\'+mode+'\\*', exclude=exclude)
