import paho.mqtt.client as mqtt
import json

from mouse_server_serial_hub.mouse.serial_mouse.serial_singleton import SerialSingleton
from mouse_server_serial_hub.mouse.shared.shared_cyclomatic_complexity_object import SharedCyclomaticComplexityObject
from mouse_server_serial_hub.mouse.shared.shared_thermal_state import SharedThermalState

serial_singleton = SerialSingleton()
shared_thermal_state = SharedThermalState()
shared_cyclomatic_complexity_object = SharedCyclomaticComplexityObject()

def on_connect(client, userdata, flags, reason_code, properties):
    print(f"Connected with result code {reason_code}")
    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("MOUSE-mqtt-bridge") # todo: topic should be more specific

def on_message(client, userdata, msg):
    if shared_thermal_state.get_thermal_state_ide() and serial_singleton is not None:
        serial_singleton.write_message(json.loads(msg.payload))


def mqtt_to_mouse_bridge():
    mqttc = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    mqttc.on_connect = on_connect
    mqttc.on_message = on_message

    mqttc.connect("test.mosquitto.org", 1883, 60)

    mqttc.loop_forever()