import os
import re

import hassapi as hass
import datetime
import git_tools

from wled_4_ha import wled_4_ha
from wled_utils.logger_utils import init_logger, get_logger

RUN_TIME_ARG = "run_time"
ENV_ARG = "env"
JOB_ARG = "job"
DATE_STR_ARG = "date_str"
VERBOSE_ARG = "verbose"
TEST_START_ARG = "test_start"
TEST_INTERVAL_ARG = "test_interval"
CONFIG_REPO_ARG = "config_repo"
CONFIG_REMOTE_ARG = "config_remote"
GIT_USERNAME = 'git_username'
GIT_PASSWORD = 'git_password'
DEFAULT_RUN_TIME = "sunset-3600"
TIME_RE_STR = '^([0-2][0-9]):([0-5][0-9]):([0-5][0-9])$'
SUN_RE_STR = '^(sunset|sunrise)([+-]*)([0-9]*)$'


# Declare Class
class Wled4Appdaemon(hass.Hass):

    def __init__(self, *args):
        super().__init__(*args)

        self.job = self.get_required_arg_value(JOB_ARG)
        self.env = self.get_required_arg_value(ENV_ARG)

        self.run_time = self.get_optional_arg_value(RUN_TIME_ARG, DEFAULT_RUN_TIME)
        self.date_str = self.get_optional_arg_value(DATE_STR_ARG, None)
        self.test_start = self.get_optional_arg_value(TEST_START_ARG, None)
        self.test_interval = self.get_optional_arg_value(TEST_INTERVAL_ARG, None)
        self.verbose = self.get_optional_arg_value(VERBOSE_ARG, False)
        self.config_repo = self.get_optional_arg_value(CONFIG_REPO_ARG, None)
        self.config_remote = self.get_optional_arg_value(CONFIG_REMOTE_ARG, None)
        self.git_username = self.get_optional_arg_value(GIT_USERNAME, None)
        self.git_password = self.get_optional_arg_value(GIT_PASSWORD, None)

        self.time_re = re.compile(TIME_RE_STR)
        self.sun_re = re.compile(SUN_RE_STR)

        init_logger(self.env, '/conf/apps/logs')

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
        self.init_mode(self.run_time)

    def init_mode(self, run_time):
        if self.test_start is None or self.test_interval is None:
            match = self.time_re.match(run_time)
            if match is not None:
                self.init_daily_mode(match.groups())
            else:
                match = self.sun_re.match(run_time.lower())
                if match is not None:
                    self.init_sun_mode(match.groups())
                else:
                    self.init_mode(DEFAULT_RUN_TIME)
        else:
            self.init_test_mode()

    def init_test_mode(self):
        self.log_info("Initializing test mode @ {start} every {interval} seconds.".format(start=self.test_start,
                                                                                     interval=self.test_interval))
        self.run_every(self.install_lights_de_jour, self.test_start, int(self.test_interval))

    def init_daily_mode(self, groups):
        self.log_info("Initializing daily mode @ {run_time}".format(run_time=self.run_time))
        run_hour = int(groups[0])
        run_min = int(groups[1])
        run_sec = int(groups[2])
        time = datetime.time(run_hour, run_min, run_sec)
        self.run_daily(self.install_lights_de_jour, time)

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
        self.run_at_sunset(self.install_lights_de_jour, offset=offset)

    def init_sunrise_mode(self, offset):
        self.log_info("Initializing sunrise mode with offset: {offset}".format(offset=offset))
        self.run_at_rise(self.install_lights_de_jour, offset=offset)

    def install_lights_de_jour(self, cb_args):
        if self.config_repo is not None:
            self.log_info("Pulling config repo @ {repo}".format(repo=self.config_repo))
            git_tools.git_pull(self.config_repo, self.config_remote, self.git_username, self.git_password)

        self.log_info("Calling wled_4_ha({job_file}, {env}, {date_str}, {verbose})".format(job_file=self.job, env=self.env,
                                                                                      date_str=self.date_str,
                                                                                      verbose=self.verbose))
        process_successful = wled_4_ha(job_file=self.job, env=self.env, date_str=self.date_str, verbose=self.verbose)
        return 0 if process_successful else 1

    def log_info(self, msg):
        get_logger.info("[{which}] - {msg)".format(which=self.env, msg=msg))
