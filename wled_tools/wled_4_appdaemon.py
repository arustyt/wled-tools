import re

import hassapi as hass
import datetime
from git import Repo, GitCommandError

from wled_4_ha import wled_4_ha
from wled_utils.logger_utils import init_logger, get_logger

DEFAULT_LOG_DIR = '/logs'
LOG_DIR = "log_dir"
ENV_ARG = "env"
JOB_ARG = "job"
RUN_DAILY_ARG = 'run_daily'
RUN_EVERY_ARG = 'run_every'
RUN_IN_ARG = 'run_in'
VERBOSE_ARG = "verbose"
CONFIG_REPO_ARG = "config_repo"
CONFIG_REMOTE_ARG = "config_remote"
GIT_USERNAME = 'git_username'
GIT_PASSWORD = 'git_password'
TIME_RE_STR = '^([0-2][0-9]):([0-5][0-9]):([0-5][0-9])$'
SUN_RE_STR = '^(sunset|sunrise)([+-]*)([0-9]*)$'


# Declare Class
class Wled4Appdaemon(hass.Hass):

    def __init__(self, *args):
        super().__init__(*args)

        self.job = self.get_required_arg_value(JOB_ARG)
        self.env = self.get_required_arg_value(ENV_ARG)

        self.run_in_cfg = self.get_optional_arg_value(RUN_IN_ARG, None)
        self.run_every_cfg = self.get_optional_arg_value(RUN_EVERY_ARG, None)
        self.run_daily_cfg = self.get_optional_arg_value(RUN_DAILY_ARG, None)
        self.verbose = self.get_optional_arg_value(VERBOSE_ARG, False)
        self.config_repo = self.get_optional_arg_value(CONFIG_REPO_ARG, None)
        self.config_remote = self.get_optional_arg_value(CONFIG_REMOTE_ARG, None)
        self.git_username = self.get_optional_arg_value(GIT_USERNAME, None)
        self.git_password = self.get_optional_arg_value(GIT_PASSWORD, None)
        self.log_dir = self.get_optional_arg_value(LOG_DIR, DEFAULT_LOG_DIR)

        self.time_re = re.compile(TIME_RE_STR)
        self.sun_re = re.compile(SUN_RE_STR)

        init_logger('wled_4_appdaemon', self.log_dir)

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

    def initialize(self):
        if self.run_in_cfg is not None:
            self.init_run_in_config(self.run_in_cfg)

        if self.run_every_cfg is not None:
            self.init_run_every_config(self.run_every_cfg)

        if self.run_daily_cfg is not None:
            self.init_run_daily_config(self.run_daily_cfg)

    def init_run_in_config(self, run_in_args):
        if run_in_args is None:
            return
        if isinstance(run_in_args, str):
            self.init_run_in(run_in_args)
        elif isinstance(run_in_args, list):
            for run_in_arg in run_in_args:
                self.init_run_in(run_in_arg)
        else:
            raise ValueError("Unsupported run-in value, {}".format(run_in_args))

    def init_run_in(self, run_in_delay):
        self.log_info('Initializing run_in @ {} seconds.'.format(run_in_delay))
        self.run_in(self.callback, int(run_in_delay))

    def init_run_every_config(self, run_every_args):
        if run_every_args is None:
            return
        if isinstance(run_every_args, str):
            self.init_run_every(run_every_args)
        elif isinstance(run_every_args, list):
            for run_every_arg in run_every_args:
                self.init_run_every(run_every_arg)
        else:
            raise ValueError("Unsupported run-every value, {}".format(run_every_args))

    def init_run_every(self, run_every_arg):
        if ',' in run_every_arg:
            parts = run_every_arg.split(',')
            start = parts[0].strip()
            interval = parts[1].strip()
        else:
            start = 'now'
            interval = run_every_arg

        self.log_info('Initializing run_every @ {}, every {} seconds.'.format(start, interval))
        self.run_every(self.callback, start, int(interval))

    def init_run_daily_config(self, run_daily_args):
        if run_daily_args is None:
            return
        if isinstance(run_daily_args, str):
            self.init_run_daily(run_daily_args)
        elif isinstance(run_daily_args, list):
            for run_daily_arg in run_daily_args:
                self.init_run_daily(run_daily_arg)
        else:
            raise ValueError("Unsupported run-every args, {}".format(run_daily_args))

    def init_run_daily(self, run_daily_arg):
        match = self.sun_re.match(run_daily_arg.lower())
        if match is not None:
            self.init_sun_mode(match.groups())
        else:
            match = self.time_re.match(run_daily_arg)
            if match is not None:
                self.init_daily_mode(match.groups())
            else:
                raise ValueError("Unsupported run-daily value, {}".format(run_daily_arg))

    def init_daily_mode(self, groups):
        run_hour = int(groups[0])
        run_min = int(groups[1])
        run_sec = int(groups[2])
        self.log_info("Initializing daily mode @ {}:{}:{}".format(run_hour, run_min, run_sec))
        time = datetime.time(run_hour, run_min, run_sec)
        self.run_daily(self.callback, time)

    def init_sun_mode(self, groups):
        sun_event = groups[0]
        offset_sign = groups[1]
        offset_value = groups[2]

        if len(offset_sign) > 0 and len(offset_value) > 0:
            offset = int('{sign}{value}'.format(sign=offset_sign, value=offset_value))

        else:
            offset = 0

        if sun_event == 'sunset':
            self.init_sunset_mode(offset)
        else:
            self.init_sunrise_mode(offset)

    def init_sunset_mode(self, offset):
        self.log_info("Initializing sunset mode with offset: {offset}".format(offset=offset))
        self.run_at_sunset(self.callback, offset=offset)

    def init_sunrise_mode(self, offset):
        self.log_info("Initializing sunrise mode with offset: {offset}".format(offset=offset))
        self.run_at_sunrise(self.callback, offset=offset)

    def callback(self, cb_args):
        self.install_presets_de_jour()

    def install_presets_de_jour(self):
        if self.config_repo is not None:
            self.log_info("Pulling config repo @ {repo}".format(repo=self.config_repo))
            try:
                repo = Repo(self.config_repo)
                # repo.username = self.git_username
                origin = repo.remotes.origin
                origin.pull()
            except GitCommandError as gce:
                self.log_error("Pulling config repo @ {repo} FAILED.".format(repo=self.config_repo))

        self.log_info("Calling wled_4_ha({job_file}, {env}, {date_str}, {verbose})".format(job_file=self.job, env=self.env,
                                                                                      date_str=self.date_str,
                                                                                      verbose=self.verbose))
        process_successful = wled_4_ha(job_file=self.job, env=self.env, date_str=self.date_str, verbose=self.verbose)
        return 0 if process_successful else 1

    def log_info(self, msg):
        get_logger().info("[{which}] - {msg}".format(which=self.env, msg=msg))

    def log_error(self, msg):
        get_logger().error("[{which}] - {msg}".format(which=self.env, msg=msg))
