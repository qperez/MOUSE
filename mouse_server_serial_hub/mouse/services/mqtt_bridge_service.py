import paho.mqtt.client as mqtt
import json
import threading

from mouse_server_serial_hub.mouse.shared.shared_haptic_service import SharedHapticService
from mouse_server_serial_hub.mouse.shared.shared_mouse_state import SharedMouseState

shared_haptic_service = SharedHapticService()
shared_mouse_state = SharedMouseState()

def on_connect(client, userdata, flags, reason_code, properties):
    print(f"Connected with result code {reason_code}")
    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("MOUSE_mqtt_bridge") # todo: topic should be more specific

def on_message(client, userdata, msg):
    msg = json.loads(msg.payload)

    if "thermal" in msg and shared_haptic_service.get_thermal_state() :
        shared_haptic_service.thermal_to_serial(
            msg["pwm_duration_thermal"], 
            msg["pwm_value_thermal"]
        )

    if "vibration" in msg and shared_haptic_service.get_vibration_state() :
            shared_haptic_service.vibration_to_serial(
                msg["pwm_duration_erm"], 
                msg["pwm_value_erm"], 
                msg.get("pwm_nb_pulse_erm", 1),
                msg.get("pwm_pulse_delay_erm", 0)
            )

    if "mouse_speed" in msg and shared_mouse_state.get_mouse_speed_state() :
        print(msg)
        shared_mouse_state.set_mouse_speed_factor(msg.get("mouse_speed_factor", 1))
        threading.Timer(msg.get("mouse_speed_duration", 3.0), reset_mouse_speed).start()

def reset_mouse_speed():
    shared_mouse_state.set_mouse_speed_factor(1.0)
    print("reset")

def mqtt_to_mouse_bridge():
    mqttc = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    mqttc.on_connect = on_connect
    mqttc.on_message = on_message

    mqttc.connect("test.mosquitto.org", 1883, 60)

    mqttc.loop_forever()