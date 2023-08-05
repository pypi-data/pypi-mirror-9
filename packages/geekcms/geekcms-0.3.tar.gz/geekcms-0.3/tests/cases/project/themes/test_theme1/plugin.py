from geekcms import protocol


class TestPlugin(protocol.BasePlugin):

    plugin = 'a'

    def run(self):
        pass

_TEST_DOC = """
Usage:
    geekcms testcmd -a -b <c> <d>
"""


class TestCLI(protocol.BaseExtendedProcedure):

    plugin = 'test_cli'

    def get_command_and_explanation(self):
        return 'testcmd', 'command for test.'

    def get_doc(self):
        return _TEST_DOC

    def run(self, args):
        return args
