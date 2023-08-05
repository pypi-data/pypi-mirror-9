# -*- coding: utf-8 -*-
from pyhammer.tasks.taskbase import TaskBase

class FilePutContentTask(TaskBase):
    def __init__( self, filename, content ):
        super(FilePutContentTask, self).__init__()
        self.__filename = filename
        self.__content = content
    
    def do( self ):
        f = open( self.__filename, 'w' )
        f.write( self.__content )
        f.close()
        return True