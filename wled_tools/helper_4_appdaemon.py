from wled_utils.logger_utils import get_logger, init_logger


DEFAULT_LOG_DIR = '/logs'
LOG_DIR = "log_dir"
ENV_ARG = "env"
MODULE = 'module'


# Declare Class
class Helper4Appdaemon:

    def __init__(self, *args):
        super().__init__(*args)
        self.args = args
        self.env = self.get_required_arg_value(ENV_ARG)
        self.log_dir = self.get_optional_arg_value(LOG_DIR, DEFAULT_LOG_DIR)
        self.module = self.get_optional_arg_value(MODULE, DEFAULT_LOG_DIR)
        init_logger(self.module, self.log_dir)

    def get_env(self):
        return self.env

    def get_log_dir(self):
        return self.log_dir

    def get_module(self):
        return self.module

    def get_optional_arg_value(self, arg_name, arg_default):
        if arg_name in self.args:
            arg_value = self.args[arg_name]
        else:
            arg_value = arg_default

        return arg_value

    def get_required_arg_value(self, arg_name):
        if arg_name in self.args:
            arg_value = self.args[arg_name]
        else:
            raise ValueError("Missing required arg: {arg}".format(arg=arg_name))

        return arg_value

    def log_info(self, msg):
        get_logger().info("[{}.{}] - {}".format(self.env, self.module, msg))

    def log_error(self, msg):
        get_logger().error("[{}.{}] - {}".format(self.env, self.module, msg))
