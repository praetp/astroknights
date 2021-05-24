import os
# import pigpio
import json
import time
import asyncio
from threading import Thread

# from lib.distance import DistanceMeasurement
# from lib.servo import ServoSteer, ServoMotor
from lib.websocket import WSServer
from lib.mpu6050Controller import mpu6050Controller# from lib.mosquitto import Mosquitto
# from lib.motorstate import MotorState
# from lib.panicstate import PanicState


#
IP=""
#IP="192.168.1.25"
context = {
#     "pi": pigpio.pi(IP),
#     "distance_front": 0,
#     "distance_back": 0,
#     "safety_on": False,
    "event_loop": asyncio.get_event_loop(),
#     "servo": {
#         "steer": {
#                 "center": 0,
#                 "spread": 0,
#                 "trim": 0
#             },
#         "motor": {
#                 "center": 0,
#                 "spread": 0,
#                 "trim": 0
#             },
#     }
}

def reset():
#     context["servo"]["steer"]["center"] = 1450
#     context["servo"]["steer"]["spread"] = 300
#     context["servo"]["steer"]["trim"] = 0
#     context["servo"]["motor"]["center"] = 1500
#     context["servo"]["motor"]["spread"] = 200
#     context["servo"]["motor"]["trim"] = 0
    pass

reset()

# context["motorstate"]=MotorState(context["servo"]["motor"])
#
# steering = ServoSteer(context)
# motor = ServoMotor(context)
#
# panicstate = PanicState(motor, context["motorstate"])
# context["panicstate"]=panicstate
#
# boosttask = 0
#
#
# def get_steer_value():
#     return steering.get_value()
#
# def get_motor_value():
#     return motor.get_value()
#
# def set_steer_value(perc, reset):
#     steering.set_value(perc, reset)
#
# def set_motor_value(perc, reset):
#     if (boosttask != 0) and boosttask.isAlive():
#         pass
#     else:
#         if context["panicstate"].get_state() == "Idle":
#             motor.set_value(perc, reset)
#         elif context["panicstate"].get_state() == "Active" and perc < 0:
#             motor.set_value(perc, reset)
#
# def update_dist_front(dist):
#     if (context["safety_on"]):
#         context["panicstate"].update_distance(dist)
#     else:
#         context["panicstate"].cancel()
#
#     context["distance_front"] = dist
#
# def update_dist_back(dist):
#     context["distance_back"] = dist
#
#
#
# class BoostTask(Thread):
#
#     def __init__(self):
#         super().__init__()
#         self._running = True
#         self._initial = True
#
#     def terminate(self):
#         self._running = False
#
#     def run(self):
#         if (self._initial):
#             motor.set_value(-100, True)
#             time.sleep(0.05)
#             motor.set_value(0, True)
#             time.sleep(0.05)
#             motor.set_value(-100, True)
#             time.sleep(0.05)
#             motor.set_value(0, True)
#             self._initial = False
#         count = 0
#         while self._running and count < 6:
#             count += 1
#             if (count < 5):
#                 print("SEND")
#                 motor.set_value(-100, True)
#             time.sleep(0.1)
#
# def startBoostTask():
#     global boosttask
#     if (boosttask != 0) and boosttask.isAlive():
#         pass
#     else:
#         boosttask = BoostTask()
#         boosttask.start()
#
#
# def backboost():
#     print("Backboost")
#     startBoostTask()
#
#
# context["callbacks"] = {
#         "get_steer_value": get_steer_value,
#         "get_motor_value": get_motor_value,
#         "set_steer_value": set_steer_value,
#         "set_motor_value": set_motor_value,
#         "backboost": backboost,
#         "reset": reset,
#     }
#
# dist1 = DistanceMeasurement(20, 21, context["pi"], update_dist_front)
# dist2 = DistanceMeasurement(26, 19, context["pi"], update_dist_back)
# dist1.start()
# dist2.start()

def cb(data):
    print (data)
    ws.updateData(data)

mpu6050Controller = mpu6050Controller(cb)
mpu6050Controller.start()
ws = WSServer(context, mpu6050Controller)
#mosq = Mosquitto(context)
#mosq.start()

try:
    asyncio.get_event_loop().run_forever()

except KeyboardInterrupt:
    mpu6050Controller.terminate()
#     dist1.terminate()
#     dist2.terminate()
#     mosq.terminate()
#     context["pi"].stop()
    pass
