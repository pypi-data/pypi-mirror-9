import os
from gears.compilers import ExecCompiler


class Babel6to5Compiler(ExecCompiler):

    result_mimetype = 'application/javascript'
    executable = 'node'
    params = [os.path.join(os.path.dirname(__file__), 'compiler.js')]

    def __init__(self, bare=False, **kwargs):
        # TODO: Add Babel options
        super(Babel6to5Compiler, self).__init__(**kwargs)

    def get_args(self):
        args = super(Babel6to5Compiler, self).get_args()
        # TODO: Add command line options here
        return args
