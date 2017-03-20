from api_classes.api_caller import ApiCaller
from exceptions import FilesSavingMethodNotDeclaredError
from exceptions import ResponseTextContentTypeError
from colors import Color
import errno
import os
import json
from cli_classes.cli_argument_builder import CliArgumentBuilder


class CliCaller:

    api_object = None
    help_description = ''
    given_args = {}
    result_msg_for_files = 'Response contains files. They were saved in the output folder ({}).'
    result_msg_for_json = '{}'
    cli_output_folder = ''
    args_to_prevent_from_being_send = ['chosen_action', 'verbose']

    def __init__(self, api_object: ApiCaller):
        self.api_object = api_object
        self.help_description = self.help_description.format(self.api_object.endpoint_url)

    def init_verbose_mode(self):
        self.result_msg_for_json = 'JSON:\n\n{}'

    def add_parser_args(self, child_parser):
        parser_argument_builder = CliArgumentBuilder(child_parser)
        parser_argument_builder.add_verbose_argument()
        parser_argument_builder.add_help_argument()

        return parser_argument_builder

    def attach_args(self, args):
        self.given_args = args.copy()
        args_to_send = args.copy()

        for arg_to_remove in self.args_to_prevent_from_being_send:
            del args_to_send[arg_to_remove]

        if 'cli_output' in args:
            self.cli_output_folder = args['cli_output']
            del args_to_send['cli_output']

        args = {k: v for k, v in args.items() if v not in [None, '']}  # Removing some 'empty' elements from dictionary

        if 'file' in args:
            self.api_object.attach_files({'file': args['file']})  # it's already stored as file handler
            del args_to_send['file']

        if self.api_object.request_method_name == ApiCaller.CONST_REQUEST_METHOD_GET:
            self.api_object.attach_params(args_to_send)
        else:  # POST
            self.api_object.attach_data(args_to_send)

    def get_colored_response_status_code(self):
        response_code = self.api_object.get_response_status_code()

        return Color.success(response_code) if response_code == 200 else Color.error(response_code)

    def get_colored_prepared_response_msg(self):
        response_msg = self.api_object.get_prepared_response_msg()
        response_msg_success_nature = self.api_object.get_response_msg_success_nature()

        return Color.success(response_msg) if response_msg_success_nature is True else Color.error(response_msg)

    def get_result_msg(self):
        if self.api_object.api_response.headers['Content-Type'] == 'text/html':
            raise ResponseTextContentTypeError('Can\'t print result, since it\'s \'text/html\' instead of expected content type with \'{}\' on board.'.format(self.api_object.api_expected_data_type))

        if self.api_object.api_expected_data_type == ApiCaller.CONST_EXPECTED_DATA_TYPE_JSON:
            return self.result_msg_for_json.format(json.dumps(self.api_object.get_response_json(), indent=4, sort_keys=True))
        elif self.api_object.api_expected_data_type == ApiCaller.CONST_EXPECTED_DATA_TYPE_FILE:
            if self.api_object.get_response_msg_success_nature() is True:
                return self.get_result_msg_for_files()
            else:
                error_msg = 'Error has occurred and your files were not saved.'
                if self.given_args['verbose'] is False:
                    error_msg += ' To get more information, please run command in verbose mode. (add \'-v\')'

                return error_msg

    def get_processed_output_path(self):
        output_path = self.cli_output_folder
        if output_path.startswith('/') is True:  # Given path is absolute
            final_output_path = output_path
        else:
            prepared_file_path = os.path.dirname(os.path.realpath(__file__)).split('/')[:-1] + [self.cli_output_folder]
            final_output_path = '/'.join(prepared_file_path)

        return final_output_path

    def get_result_msg_for_files(self):
        return self.result_msg_for_files.format(self.get_processed_output_path())

    def do_post_processing(self):
        if self.api_object.api_expected_data_type == ApiCaller.CONST_EXPECTED_DATA_TYPE_FILE:
            file_saving_function = getattr(self, 'save_files', None)
            if not callable(file_saving_function):
                raise FilesSavingMethodNotDeclaredError('Can\'t do post processing, since method \'save_files\' is not declared in {} class.'.format(self.__class__.__name__))

            if self.api_object.get_response_status_code() == 200 and self.api_object.get_response_msg_success_nature() is True:
                self.create_output_dir()
                file_saving_function()

    def create_output_dir(self):
        try:
            os.makedirs(self.cli_output_folder)
        except OSError as exc:
            if exc.errno == errno.EEXIST and os.path.isdir(self.cli_output_folder):
                pass
            elif exc.errno == errno.EACCES:
                raise Exception('Failed to create directory in \'{}\'. Possibly it\'s connected with file rights.'.format(self.get_processed_output_path()))
            else:
                raise
