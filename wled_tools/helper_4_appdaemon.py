from wled_utils.logger_utils import get_logger, init_logger


DEFAULT_LOG_DIR = '/logs'
LOG_DIR_ARG = "log_dir"
ENV_ARG = "env"
MODULE_ARG = 'module'


# Declare Class
class Helper4Appdaemon:

    def __init__(self, *args):
        # Extracting configuration from argument list of calling constructor.
        self.app_name = args[0][2]
        self.config = args[0][3]
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
        if arg_name in self.config:
            arg_value = self.config[arg_name]
        else:
            arg_value = arg_default

        return arg_value

    def get_required_arg_value(self, arg_name):
        if arg_name in self.config:
            arg_value = self.config[arg_name]
        else:
            raise ValueError("Missing required arg: {}".format(arg_name))

        return arg_value

    def log_info(self, msg):
        get_logger().info("[{}.{}] - {}".format(self.module, self.app_name, msg))

    def log_error(self, msg):
        get_logger().error("[{}.{}] - {}".format(self.module, self.app_name, msg))
