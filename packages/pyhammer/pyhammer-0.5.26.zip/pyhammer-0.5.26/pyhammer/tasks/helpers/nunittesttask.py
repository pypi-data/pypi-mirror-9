# -*- coding: utf-8 -*-
import os
from pyhammer.tasks.taskbase import TaskBase
from pyhammer.utils import execProg

class NUnitTestTask(TaskBase):
    """NUnit Test Run Step"""

    def __init__( self, csTestDllPath ):
        super(NUnitTestTask, self).__init__()

        self.command = """nunit-console \"%s\"""" % ( csTestDllPath )
        self.csTestDllPath = csTestDllPath

    def do( self ):
        self.reporter.message( "RUN CS NUNIT TEST: %s" % self.csTestDllPath )

        print(self.command)

        result = execProg( self.command, self.reporter, os.path.dirname(self.csTestDllPath) ) == 0
        return result