from appdaemon_tools.actions_4_appdaemon import install_presets_de_jour, send_current_holiday_to_ha
from appdaemon_tools.ha_4_appdaemon import Ha4Appdaemon


class Wled4Appdaemon(Ha4Appdaemon):

    def __init__(self, *args):
        super().__init__(*args)

    def initialize(self):
        super().initialize()

    def callback(self, cb_args):
        super().callback(cb_args)
        install_presets_de_jour(job=self.job, env=self.helper.get_env(), date_str=self.date_str,
                                verbose=self.verbose, helper=self.helper)
        send_current_holiday_to_ha(job=self.job, env=self.helper.get_env(), date_str=self.date_str,
                                   verbose=self.verbose, helper=self.helper, mqttapi=self.mqtt)
