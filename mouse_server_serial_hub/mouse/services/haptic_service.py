# from time import sleep

# from mouse_server_serial_hub.mouse.serial_mouse.serial_singleton import SerialSingleton
# from mouse_server_serial_hub.mouse.shared.shared_haptic_service import SharedHapticState

# serial_singleton = SerialSingleton()

# def vibrate(duration = 100, pwm = 100, pulse = 1):
#     if not SharedHapticState.get_vibration_state(): return
        
#     json_values = {
#             "pwm_duration_erm": duration,
#             "pwm_value_erm": pwm,
#             "pwm_nb_pulse_erm": pulse
#     }
#     if serial_singleton is not None:
#         serial_singleton.write_message(json_values)


# def heat(duration = 1000, pwm = 100):
#     if not SharedHapticState.get_thermal_state(): return

#     json_values = {
#             "pwm-duration-thermal": duration,
#             "pwm-value-thermal": pwm,
#     }
#     if serial_singleton is not None:
#         serial_singleton.write_message(json_values)


# # shared_haptic_state = SharedHapticState()

# # def haptic_over_serial_thread():

# #     json_values = {
# #         "pwm-value-thermal": 0,
# #         "pwm-value-erm": 0,
# #         "pwm_nb_pulse_erm": 0
# #     }
    
# #     while True:
# #         if serial_singleton is not None:
# #             if shared_haptic_state.get_thermal_state() :
# #                 json_values["pwm-value-thermal"] = shared_haptic_state.get_pwm_value_thermal()
# #             else :
# #                 json_values["pwm-value-thermal"] = 0
            
# #             if shared_haptic_state.get_vibration_state() :
# #                 json_values["pwm-value-erm"] = shared_haptic_state.get_pwm_value_erm()
# #                 json_values["pwm_nb_pulse_erm"] = shared_haptic_state.get_pwm_nb_pulse_erm()
# #             else :
# #                 json_values["pwm-value-erm"] = 0
# #                 json_values["pwm_nb_pulse_erm"] = 0

# #             serial_singleton.write_message(json_values)

# #         sleep(0.5)
