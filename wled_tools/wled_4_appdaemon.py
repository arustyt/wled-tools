from ha_4_appdaemon import Ha4Appdaemon
from wled_4_ha import wled_4_ha
from wled_constants import RESULT_KEY


class Wled4Appdaemon(Ha4Appdaemon):

    def __init__(self, *args):
        super().__init__(*args)

    def initialize(self):
        super().initialize()

    def callback(self, cb_args):
        self.install_presets_de_jour(job=self.job, env=self.helper.get_env(), date_str=self.date_str,
                                     verbose=self.verbose, helper=self.helper)

    @staticmethod
    def install_presets_de_jour(job=None, env=None, date_str=None, verbose=False, helper=None):
        helper.log_info(
            "Calling wled_4_ha({}, {}, {}, {})".format(job, env, date_str, verbose))
        result = wled_4_ha(job_file=job, env=env, date_str=date_str, verbose=verbose)
        process_successful = result[RESULT_KEY]
        return 0 if process_successful else 1
