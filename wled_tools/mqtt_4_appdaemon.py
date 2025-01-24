import json
from abc import abstractmethod

import mqttapi as mqtt
import hassapi as hass

from appdaemon_tools.appdaemon_actions import send_current_holiday_to_ha, install_presets_de_jour
from appdaemon_tools.ha_4_appdaemon import JOB_ARG, VERBOSE_ARG
from appdaemon_tools.helper_4_appdaemon import Helper4Appdaemon, ENV_ARG

DEFAULT_APPDAEMON_CMD_TOPIC = 'appdaemon/cmd'
APPDAEMON_CMD_TOPIC_TAG = "cmd_topic"
APPDAEMON_NAMESPACE_TAG = "namespace"

ACTION_MAP = { 'send_holiday': send_current_holiday_to_ha, 'install_presets': install_presets_de_jour}

APPDAEMON_APP_TAG = 'app'
APPDAEMON_ACTION_TAG = 'action'


# MQTT Message Payload
# {'app': 'wled_roof',
#  'action': 'send_holiday' | 'install_presets'}


class Mqtt4Appdaemon(hass.Hass):

    def __init__(self, *args):
        super().__init__(*args)
        self.mqtt = None
        self.helper = Helper4Appdaemon(args)
        self.namespace = self.helper.get_optional_arg_value(APPDAEMON_NAMESPACE_TAG, None)

    @abstractmethod
    def initialize(self):
        self.mqtt = self.get_plugin_api("MQTT")
        self.mqtt.set_namespace(self.namespace)
        self.mqtt.listen_event(self.process_mqtt_event, namespace=self.namespace)

    def process_mqtt_event(self, event_name, data, cb_args):
        if event_name == 'MQTT_MESSAGE':
            payload_str = data['payload']
            payload = json.loads(payload_str)
            app = payload[APPDAEMON_APP_TAG]
            action = payload[APPDAEMON_ACTION_TAG]
            app_data = self.helper.app_config[app]
            job = app_data[JOB_ARG]
            env = app_data[ENV_ARG]
            verbose = self.helper.get_optional_arg_value(VERBOSE_ARG, False)

            if action == 'send_holiday':
                send_current_holiday_to_ha(job=job, env=env, verbose=verbose, helper=self.helper, mqttapi=self.mqtt)
                return
            elif action == 'install_presets':
                install_presets_de_jour(job=job, env=env, verbose=verbose, helper=self.helper)
                return

        self.helper.log_info("GOT UNHANDLED EVENT: event_name: {}, data: {}".format(event_name, data))
