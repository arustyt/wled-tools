import datetime
import re
from abc import abstractmethod

import hassapi as hass
from git import Repo, GitCommandError

from helper_4_appdaemon import Helper4Appdaemon

JOB_ARG = "job"
RUN_DAILY_ARG = 'run_daily'
RUN_HOURLY_ARG = 'run_hourly'
RUN_EVERY_ARG = 'run_every'
RUN_IN_ARG = 'run_in'
DATE_STR_ARG = "date_str"
VERBOSE_ARG = "verbose"
CONFIG_REPO_ARG = "config_repo"
CONFIG_REMOTE_ARG = "config_remote"
GIT_USERNAME = 'git_username'
GIT_PASSWORD = 'git_password'
TIME_RE_STR = '^([0-2][0-9]):([0-5][0-9]):([0-5][0-9])$'
SUN_RE_STR = '^(sunset|sunrise)([+-]*)([0-9]*)$'


# Declare Class
class Ha4Appdaemon(hass.Hass):

    def __init__(self, *args):
        super().__init__(*args)

        self.helper = Helper4Appdaemon(args)
        self.job = self.helper.get_required_arg_value(JOB_ARG)

        self.run_in_cfg = self.helper.get_optional_arg_value(RUN_IN_ARG, None)
        self.run_every_cfg = self.helper.get_optional_arg_value(RUN_EVERY_ARG, None)
        self.run_daily_cfg = self.helper.get_optional_arg_value(RUN_DAILY_ARG, None)
        self.run_hourly_cfg = self.helper.get_optional_arg_value(RUN_HOURLY_ARG, None)
        self.date_str = self.helper.get_optional_arg_value(DATE_STR_ARG, None)
        self.verbose = self.helper.get_optional_arg_value(VERBOSE_ARG, False)
        self.config_repo = self.helper.get_optional_arg_value(CONFIG_REPO_ARG, None)
        self.config_remote = self.helper.get_optional_arg_value(CONFIG_REMOTE_ARG, None)
        self.git_username = self.helper.get_optional_arg_value(GIT_USERNAME, None)
        self.git_password = self.helper.get_optional_arg_value(GIT_PASSWORD, None)

        self.time_re = re.compile(TIME_RE_STR)
        self.sun_re = re.compile(SUN_RE_STR)
        self.mqtt = None

    @abstractmethod
    def initialize(self):
        self.mqtt = self.get_plugin_api("MQTT")

        if self.run_in_cfg is not None:
            self.init_run_in_config(self.run_in_cfg)

        if self.run_every_cfg is not None:
            self.init_run_every_config(self.run_every_cfg)

        if self.run_daily_cfg is not None:
            self.init_run_daily_config(self.run_daily_cfg)

        if self.run_hourly_cfg is not None:
            self.init_run_hourly_config(self.run_hourly_cfg)

    def init_run_in_config(self, run_in_args):
        if run_in_args is None:
            return
        if isinstance(run_in_args, int):
            self.init_run_in(run_in_args)
        elif isinstance(run_in_args, str):
            self.init_run_in(int(run_in_args))
        elif isinstance(run_in_args, list):
            for run_in_arg in run_in_args:
                self.init_run_in(int(run_in_arg))
        else:
            raise ValueError("Unsupported run-in value, {}".format(run_in_args))

    def init_run_in(self, run_in_delay):
        self.helper.log_info('Initializing run_in @ {} seconds.'.format(run_in_delay))
        self.run_in(self.callback, run_in_delay)

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

        self.helper.log_info('Initializing run_every @ {}, every {} seconds.'.format(start, interval))
        self.run_every(self.callback, start, int(interval))

    def init_run_hourly_config(self, run_hourly_args):
        if run_hourly_args is None:
            return
        if isinstance(run_hourly_args, str):
            self.init_run_every(run_hourly_args)
        elif isinstance(run_hourly_args, list):
            for run_every_arg in run_hourly_args:
                self.init_run_every(run_every_arg)
        else:
            raise ValueError("Unsupported run-every value, {}".format(run_hourly_args))

    def init_run_hourly(self, run_hourly_arg):
        if ',' in run_hourly_arg:
            run_times = run_hourly_arg.split(',')
        else:
            run_times = [run_hourly_arg]

        for run_time in run_times:
            self.helper.log_info('Initializing run_hourly @ {} minutes past the hour.'.format(run_time))
            if ':' in run_time:
                hms = run_time.split(':')
                minutes = int(hms[1])
            else:
                minutes = int(run_time)

            runtime = datetime.time(0, minutes, 0)
            self.run_hourly(self.callback, runtime)

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
        self.helper.log_info("Initializing daily mode @ {}:{}:{}".format(run_hour, run_min, run_sec))
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
        self.helper.log_info("Initializing sunset mode with offset: {offset}".format(offset=offset))
        self.run_at_sunset(self.callback, offset=offset)

    def init_sunrise_mode(self, offset):
        self.helper.log_info("Initializing sunrise mode with offset: {offset}".format(offset=offset))
        self.run_at_sunrise(self.callback, offset=offset)

    @abstractmethod
    def callback(self, cb_args):
        self.pull_config_repo()

    def pull_config_repo(self):
        if self.config_repo is not None:
            self.helper.log_info("Pulling config repo @ {repo}".format(repo=self.config_repo))
            try:
                repo = Repo(self.config_repo)
                # repo.username = self.git_username
                origin = repo.remotes.origin
                origin.pull()
            except GitCommandError as gce:
                self.helper.log_error("Pulling config repo @ {repo} FAILED.".format(repo=self.config_repo))
