import json

from wled_4_ha import wled_4_ha, RESULT_KEY, CANDIDATES_KEY, HOLIDAY_KEY
from wled_base_4_appdaemon import WledBase4Appdaemon
from wled_constants import PRESETS_KEY
from wled_utils.logger_utils import init_logger

MQTT_PLUGIN_NAMESPACE = "mqtt"  # matches appdeamon.yaml
WLED_HOLIDAY_TOPIC = 'wled/{}/holiday'


class WledHoliday4Appdaemon(WledBase4Appdaemon):

    def __init__(self, *args):
        super().__init__(*args)
        self.mqtt = None
        init_logger('wled_holiday_4_appdaemon', self.log_dir)

    def initialize(self):
        super().initialize()
        self.mqtt = self.get_plugin_api("MQTT")

    def callback(self, cb_args):
        self.send_current_holiday_to_ha()

    def send_current_holiday_to_ha(self):
        holidays_only = True
        self.log_info(
            "Calling wled_4_ha({}, {}, {}, {}, holidays_only={})".format(self.job, self.env, self.date_str,
                                                                         self.verbose, holidays_only))
        result = wled_4_ha(job_file=self.job, env=self.env, date_str=self.date_str, verbose=self.verbose,
                           holidays_only=holidays_only)
        process_successful = result[RESULT_KEY]
        if process_successful:
            self.send_via_mqtt(candidates=result[CANDIDATES_KEY], holiday_name=result[HOLIDAY_KEY],
                               presets=result[PRESETS_KEY])
            return 0
        else:
            return 1

    def send_via_mqtt(self, *, candidates, holiday_name, presets):
        payload_data = {CANDIDATES_KEY: candidates, HOLIDAY_KEY: holiday_name, PRESETS_KEY: presets}
        payload = json.dumps(payload_data)
        self.log_info("type(self.mqtt): {}".format(type(self.mqtt)))
        self.mqtt.Mqtt.mqtt_publish(
            WLED_HOLIDAY_TOPIC.format(self.env),
            payload=payload,
            namespace=MQTT_PLUGIN_NAMESPACE)
