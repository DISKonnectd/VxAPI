from cli_classes.cli_caller import CliCaller
from cli_classes.cli_argument_builder import CliArgumentBuilder


class CliState(CliCaller):

    help_description = 'Get the state of an analysis by \'{}\''

    def add_parser_args(self, child_parser):
        parser_argument_builder = super(CliState, self).add_parser_args(child_parser)
        parser_argument_builder.add_sha256_argument()
        parser_argument_builder.add_environment_id_argument()
