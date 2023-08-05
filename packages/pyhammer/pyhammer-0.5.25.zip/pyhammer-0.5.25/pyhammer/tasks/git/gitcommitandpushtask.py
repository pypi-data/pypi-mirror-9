# -*- coding: utf-8 -*-
from pyhammer.tasks.taskbase import TaskBase
from pyhammer.utils import execProg

class GitCommitAndPushTask(TaskBase):
    def __init__( self, dir, add ):
        super(GitCommitAndPushTask, self).__init__()
        
        self.__dir = dir
        self.__add = add

    def do( self ):
        self.reporter.message( "Git Commit and Push: %s" % self.__dir )
        addResult = True
        if self.__add:
            command = "git add *"
            addResult = execProg( command, self.reporter, self.__dir ) == 0

        commitResult = True
        if addResult :
            commitMessage = "Commited by Build"
            command = "git commit -m \"%s\"" % commitMessage
            self.reporter.message( command )
            commitResult = execProg( command, self.reporter, self.__dir ) == 0

        if not commitResult:
            return False

        command = "git push"
        self.reporter.message( command )
        return execProg( command, self.reporter, self.__dir ) == 0