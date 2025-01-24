from abc import abstractmethod

import mqttapi as mqtt
import hassapi as hass

from appdaemon_tools.appdaemon_actions import send_current_holiday_to_ha, install_presets_de_jour
from appdaemon_tools.helper_4_appdaemon import Helper4Appdaemon

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
        self.cmd_topic = self.helper.get_required_arg_value(APPDAEMON_CMD_TOPIC_TAG)
        self.namespace = self.helper.get_optional_arg_value(APPDAEMON_NAMESPACE_TAG, None)

    @abstractmethod
    def initialize(self):
        self.mqtt = self.get_plugin_api("MQTT")
        if self.namespace is not None:
            self.try_with_namespace()
        else:
            self.try_without_namespace()

    def try_without_namespace(self):
        try:
            self.helper.log_info(
                "Trying self.mqtt.mqtt_subscribe({})".format(self.cmd_topic))
            self.mqtt_subscribe(self.cmd_topic)
            self.helper.log_info(
                "Trying self.mqtt.mqtt_subscribe({})".format(self.cmd_topic))
            self.mqtt_subscribe(self.cmd_topic)
        except Exception as ex:
            self.helper.log_error(
                "Trying self.mqtt.mqtt_subscribe({}) - FAILED".format(self.cmd_topic))
        try:
            self.helper.log_info(
                "Trying self.call_service({}, topic={})".format("mqtt/subscribe", self.cmd_topic))
            self.call_service("mqtt/subscribe", topic=self.cmd_topic)
        except Exception as ex:
            self.helper.log_error(
                "Trying self.call_service({}, topic={}) - FAILED".format("mqtt/subscribe", self.cmd_topic))
        self.listen_event(self.process_mqtt_event)

    def try_with_namespace(self):
        self.set_namespace(self.namespace)
        try:
            self.helper.log_info(
                "Trying self.mqtt.mqtt_subscribe({}, namespace={})".format(self.cmd_topic, self.namespace))
            self.mqtt_subscribe(self.cmd_topic, namespace=self.namespace)
            self.helper.log_info(
                "Trying self.mqtt.mqtt_subscribe({}, namespace={})".format(self.cmd_topic, self.namespace))
            self.mqtt_subscribe(self.cmd_topic, namespace=self.namespace)
        except Exception as ex:
            self.helper.log_error(
                "Trying self.mqtt.mqtt_subscribe({}, namespace={} - FAILED)".format(self.cmd_topic, self.namespace))
        try:
            self.helper.log_info(
                "Trying self.call_service({}, topic={}, namespace={})".format("mqtt/subscribe", self.cmd_topic,
                                                                              self.namespace))
            self.call_service("mqtt/subscribe", topic=self.cmd_topic, namespace=self.namespace)
        except Exception as ex:
            self.helper.log_error(
                "Trying self.call_service({}, topic={}, namespace={} - FAILED)".format("mqtt/subscribe", self.cmd_topic,
                                                                                       self.namespace))
        self.listen_event(self.process_mqtt_event, namespace=self.namespace)

    def process_mqtt_event(self, event_name, data, cb_args):
        if event_name != 'state_changed':
            self.helper.log_info("GOT EVENT: event_name: {}, data: {}".format(event_name, data))
