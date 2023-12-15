import os
import re

import hassapi as hass
import datetime
import git_tools

from wled_4_ha import wled_4_ha

RUN_TIME_ARG = "run_time"
ENV_ARG = "env"
JOB_ARG = "job"
DATE_STR_ARG = "date_str"
VERBOSE_ARG = "verbose"
TEST_START_ARG = "test_start"
TEST_INTERVAL_ARG = "test_interval"
CONFIG_REPO_ARG = "config_repo"
DEFAULT_RUN_TIME = "sunset-3600"
TIME_RE_STR = '^([0-2][0-9]):([0-5][0-9]):([0-5][0-9])$'
SUN_RE_STR = '^(sunset|sunrise)([+-]*)([0-9]*)$'


# Declare Class
class Wled4Appdaemon(hass.Hass):

    def __init__(self, *args):
        super().__init__(*args)
        if RUN_TIME_ARG in self.args:
            self.run_time = self.args[RUN_TIME_ARG]
        else:
            self.run_time = DEFAULT_RUN_TIME

        if DATE_STR_ARG in self.args:
            self.date_str = self.args[DATE_STR_ARG]
        else:
            self.date_str = None

        if TEST_START_ARG in self.args:
            self.test_start = self.args[TEST_START_ARG]
        else:
            self.test_start = None

        if TEST_INTERVAL_ARG in self.args:
            self.test_interval = self.args[TEST_INTERVAL_ARG]
        else:
            self.test_interval = None

        if VERBOSE_ARG in self.args:
            self.verbose = self.args[VERBOSE_ARG]
        else:
            self.verbose = False

        if CONFIG_REPO_ARG in self.args:
            self.config_repo = self.args[CONFIG_REPO_ARG]
        else:
            self.config_repo = None

        self.job = self.args[JOB_ARG]
        self.env = self.args[ENV_ARG]

        self.time_re = re.compile(TIME_RE_STR)
        self.sun_re = re.compile(SUN_RE_STR)

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
        self.log("Initializing test mode @ {start} every {interval} seconds.".format(start=self.test_start,
                                                                                     interval=self.test_interval))
        self.run_every(self.install_lights_de_jour, self.test_start, int(self.test_interval))

    def init_daily_mode(self, groups):
        self.log("Initializing daily mode @ {run_time}".format(run_time=self.run_time))
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
        self.log("Initializing sunset mode with offset: {offset}".format(offset=offset))
        self.run_at_sunset(self.install_lights_de_jour, offset=offset)

    def init_sunrise_mode(self, offset):
        self.log("Initializing sunrise mode with offset: {offset}".format(offset=offset))
        self.run_at_rise(self.install_lights_de_jour, offset=offset)

    def install_lights_de_jour(self, cb_args):
        if self.config_repo is not None:
            self.log("Pulling config repo @ {repo}".format(repo=self.config_repo))
            git_tools.git_pull(self.config_repo)

        self.log("Calling wled_4_ha({job_file}, {env}, {date_str}, {verbose})".format(job_file=self.job, env=self.env,
                                                                                      date_str=self.date_str,
                                                                                      verbose=self.verbose))
        process_successful = wled_4_ha(job_file=self.job, env=self.env, date_str=self.date_str, verbose=self.verbose)
        return 0 if process_successful else 1

