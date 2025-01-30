from wled_utils.logger_utils import get_logger, init_logger


DEFAULT_LOG_DIR = '/logs'
LOG_DIR_ARG = "log_dir"
ENV_ARG = "env"
MODULE_ARG = 'module'


# Declare Class
class Helper4Appdaemon:

    def __init__(self, *args):
        # Extracting configuration from argument list of calling constructor.
        self.app_name = args[0][1]
        self.app_args = args[0][3]
        self.appdaemon_config = args[0][4]
        self.app_config = args[0][5]
        self.global_vars = args[0][6]
        ##
        self.env = self.get_required_arg_value(ENV_ARG)
        self.module = self.get_required_arg_value(MODULE_ARG)
        self.log_dir = self.get_optional_arg_value(LOG_DIR_ARG, DEFAULT_LOG_DIR)
        init_logger(self.module, self.log_dir)

    def get_env(self):
        return self.env

    def get_log_dir(self):
        return self.log_dir

    def get_module(self):
        return self.module

    def get_optional_arg_value(self, arg_name, arg_default):
        return self.get_config_value(self.app_args, None, arg_name, arg_default, required=False)

    def get_required_arg_value(self, arg_name):
        return self.get_config_value(self.app_args, None, arg_name)

    def get_optional_app_config_value(self, app_name, arg_name, arg_default):
        return self.get_config_value(self.app_config, app_name, arg_name, arg_default, required=False)

    def get_required_app_config_value(self, app_name, arg_name):
        return self.get_config_value(self.app_config, app_name, arg_name)

    def get_optional_appdaemon_config_value(self, section, arg_name, arg_default):
        return self.get_config_value(self.appdaemon_config, section, arg_name, arg_default, required=False)

    def get_required_appdaemon_config_value(self, section, arg_name):
        return self.get_config_value(self.appdaemon_config, section, arg_name)

    @staticmethod
    def get_config_value(config_values, section, arg_name, arg_default=None, required=True):
        if section is not None:
            if isinstance(section, list):
                if len(section) > 0:
                    return Helper4Appdaemon.get_config_value(config_values[section[0]], section[1:],
                                                             arg_default, arg_name)
            elif isinstance(section, str):
                if len(section) > 0:
                    if '.' in section:
                        parts = section.split('.')
                        this_section = parts[0]
                        remaining_sections = parts[1:]
                        return Helper4Appdaemon.get_config_value(config_values[this_section],
                                                                 remaining_sections, arg_default, arg_name)
                    else:
                        return Helper4Appdaemon.get_config_value(config_values[section], None,
                                                                 arg_default, arg_name)

        if arg_name in config_values:
            arg_value = config_values[arg_name]
        else:
            if not required:
                arg_value = arg_default
            else:
                raise ValueError("Missing required arg: {}".format(arg_name))
        return arg_value

    def log_info(self, msg):
        get_logger().info("[{}.{}] - {}".format(self.module, self.app_name, msg))

    def log_error(self, msg):
        get_logger().error("[{}.{}] - {}".format(self.module, self.app_name, msg))

    def log_warning(self, msg):
        get_logger().warning("[{}.{}] - {}".format(self.module, self.app_name, msg))
