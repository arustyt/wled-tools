import json
from abc import abstractmethod

import mqttapi as mqtt
import hassapi as hass

from appdaemon_tools.appdaemon_actions import send_current_holiday_to_ha, install_presets_de_jour, pull_config_repo
from appdaemon_tools.ha_4_appdaemon import JOB_ARG, VERBOSE_ARG, CONFIG_REPO_ARG
from appdaemon_tools.helper_4_appdaemon import Helper4Appdaemon, ENV_ARG

SEND_HOLIDAY_ACTION = 'send_holiday'
INSTALL_PRESETS_ACTION = 'install_presets'
PULL_CONFIG_ACTION = 'pull_config'

DEFAULT_APPDAEMON_CMD_TOPIC = 'appdaemon/cmd'
APPDAEMON_CMD_TOPIC_TAG = "cmd_topic"
APPDAEMON_NAMESPACE_TAG = "namespace"

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
            config_repo = app_data[CONFIG_REPO_ARG]
            verbose = self.helper.get_optional_arg_value(VERBOSE_ARG, False)

            if action == SEND_HOLIDAY_ACTION:
                send_current_holiday_to_ha(job=job, env=env, verbose=verbose, helper=self.helper, mqttapi=self.mqtt)
                return
            elif action == INSTALL_PRESETS_ACTION:
                install_presets_de_jour(job=job, env=env, verbose=True, helper=self.helper)
                return
            elif action == PULL_CONFIG_ACTION:
                pull_config_repo(config_repo, verbose=True, helper=self.helper)
                return

        self.helper.log_warning("GOT UNHANDLED EVENT: event_name: {}, data: {}".format(event_name, data))
