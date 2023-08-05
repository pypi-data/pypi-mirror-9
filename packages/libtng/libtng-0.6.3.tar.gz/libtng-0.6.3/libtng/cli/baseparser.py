import argparse

from libtng.module_loading import import_string


class BaseParser(object):
    """
    Command-line argument parser base class that registers all
    subcommands.
    """

    def __init__(self, program_name=""):
        self._parser = argparse.ArgumentParser() if not program_name\
            else argparse.ArgumentParser(program_name)
        self._subparsers = self._parser.add_subparsers(dest="subparser_name")


    def register_commands(self, command_list):
        """Registers commands to the base parser.

        Args:
            command_list: a list of strings specifying the dotted
                path to modules holding commands.

        Returns:
            None
        """
        for module_path in command_list:
            command = import_string(module_path + '.Command')()
            command.add_to_subparsers(self._subparsers)

    def parse_args(self, *args, **kwargs):
        return self._parser.parse_args()


parser = BaseParser()