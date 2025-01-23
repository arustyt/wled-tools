from abc import abstractmethod

import mqttapi as mqtt

from appdaemon_tools.appdaemon_actions import send_current_holiday_to_ha, install_presets_de_jour
from appdaemon_tools.helper_4_appdaemon import Helper4Appdaemon

DEFAULT_APPDAEMON_CMD_TOPIC = 'appdaemon/cmd'
APPDAEMON_CMD_TOPIC = "appdaemon_cmd_topic"

ACTION_MAP = { 'send_holiday': send_current_holiday_to_ha, 'install_presets': install_presets_de_jour}

APPDAEMON_APP_TAG = 'app'
APPDAEMON_ACTION_TAG = 'action'


# MQTT Message Payload
# {'app': 'wled_roof',
#  'action': 'send_holiday' | 'install_presets'}


class Mqtt4Appdaemon(mqtt.Mqtt):

    def __init__(self, *args):
        super().__init__(*args)

        self.helper = Helper4Appdaemon(args)
        self.cmd_topic = self.helper.get_optional_arg_value(APPDAEMON_CMD_TOPIC, DEFAULT_APPDAEMON_CMD_TOPIC)

    @abstractmethod
    def initialize(self):
        self.mqtt_subscribe(self.cmd_topic)
        self.listen_event(self.process_mqtt_event)

    def process_mqtt_event(self, event_name, data, cb_args):
        self.helper.log_info("GOT EVENT: event_name: {}, data: {}".format(event_name, data))
