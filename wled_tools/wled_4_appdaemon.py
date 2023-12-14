import hassapi as hass
import datetime

from wled_4_ha import wled_4_ha

RUN_TIME = "run_time"
ENV = "env"
JOB = "job"
DATE_STR = "date_str"
VERBOSE = "verbose"
TEST_START = "test_start"
TEST_INTERVAL = "test_interval"


# Declare Class
class WledLightsLoader(hass.Hass):

    def __init__(self, *args):
        super().__init__(*args)
        if RUN_TIME in self.args:
            self.run_time = self.args[RUN_TIME]
        else:
            self.run_time = "12:00:00"

        if DATE_STR in self.args:
            self.date_str = self.args[DATE_STR]
        else:
            self.date_str = None

        if TEST_START in self.args:
            self.test_start = self.args[TEST_START]
        else:
            self.test_start = None

        if TEST_INTERVAL in self.args:
            self.test_interval = self.args[TEST_INTERVAL]
        else:
            self.test_interval = None

        if VERBOSE in self.args:
            self.verbose = self.args[VERBOSE]
        else:
            self.verbose = False

        self.job = self.args[JOB]
        self.env = self.args[ENV]

    def initialize(self):

        if self.test_start is None or self.test_interval is None:
            self.log("Initializing daily mode @ {run_time}".format(run_time=self.run_time))
            run_time_parts = self.run_time.split(':')
            run_hour = int(run_time_parts[0])
            run_min = int(run_time_parts[1])
            run_sec = int(run_time_parts[2])
            time = datetime.time(run_hour, run_min, run_sec)
            self.run_daily(self.install_lights_de_jour, time)
        else:
            self.log("Initializing test mode @ {start} every {interval} seconds.".format(start=self.test_start,
                                                                                         interval=self.test_interval))
            self.run_every(self.install_lights_de_jour, self.test_start, int(self.test_interval))

    def install_lights_de_jour(self, cb_args):
        self.log("Calling wled_4_ha({job_file}, {env}, {date_str}, {verbose})".format(job_file=self.job, env=self.env,
                                                                                      date_str=self.date_str,
                                                                                      verbose=self.verbose))
        process_successful = wled_4_ha(job_file=self.job, env=self.env, date_str=self.date_str, verbose=self.verbose)
        return 0 if process_successful else 1
