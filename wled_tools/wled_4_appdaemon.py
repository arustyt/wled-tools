from ha_4_appdaemon import Ha4Appdaemon
from wled_4_ha import wled_4_ha
from wled_constants import RESULT_KEY


class Wled4Appdaemon(Ha4Appdaemon):

    def __init__(self, *args):
        super().__init__(*args)

    def initialize(self):
        super().initialize()

    def callback(self, cb_args):
        self.install_presets_de_jour()

    def install_presets_de_jour(self):
        self.helper.log_info(
            "Calling wled_4_ha({}, {}, {}, {})".format(self.job, self.helper.get_env(), self.date_str, self.verbose))
        result = wled_4_ha(job_file=self.job, env=self.helper.get_env(), date_str=self.date_str, verbose=self.verbose)
        process_successful = result[RESULT_KEY]
        return 0 if process_successful else 1
