import hassapi as hass
import datetime

from wled_4_ha import wled_4_ha

RUN_TIME = "run_time"
ENV = "env"
JOB = "job"
DATE_STR = "date_str"
VERBOSE = "verbose"


# Declare Class
class WledLightsLoader(hass.Hass):

    def __init__(self):
        super().__init__()
        if RUN_TIME in self.args:
            self.run_time = self.args[RUN_TIME]
        else:
            self.run_time = "12:00:00"

        if DATE_STR in self.args:
            self.date_str = self.args[DATE_STR]
        else:
            self.date_str = None

        if VERBOSE in self.args:
            self.verbose = self.args[VERBOSE]
        else:
            self.verbose = False

        self.job = self.args[JOB]
        self.env = self.args[ENV]

    def initialize(self):
        run_time_parts = self.run_time.split(':')
        run_hour = int(run_time_parts[0])
        run_min = int(run_time_parts[1])
        run_sec = int(run_time_parts[2])

        time = datetime.time(run_hour, run_min, run_sec)
        self.run_daily(self.install_lights_de_jour, time)

    def install_lights_de_jour(self, cb_args):
        process_successful = wled_4_ha(job_file=self.job, env=self.env, date_str=self.date_str, verbose=self.verbose)
        return 0 if process_successful else 1
