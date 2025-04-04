from appdaemon_tools.appdaemon_actions import send_current_holiday_to_ha
from appdaemon_tools.ha_4_appdaemon import Ha4Appdaemon


class WledHoliday4Appdaemon(Ha4Appdaemon):

    def __init__(self, *args):
        super().__init__(*args)
        self.mqtt = None

    def initialize(self):
        super().initialize()
        self.mqtt = self.get_plugin_api("MQTT")

    def callback(self, cb_args):
        super().callback(cb_args)
        send_current_holiday_to_ha(job=self.job, env=self.helper.get_env(), date_str=self.date_str,
                                   verbose=self.verbose, helper=self.helper, mqttapi=self.mqtt)
