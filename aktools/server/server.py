import json
import time
import tornado
import asyncio

from lib.wsHandler import wsHandler
#from lib.mpu6050Controller import mpu6050Controller# from lib.mosquitto import Mosquitto
from lib.streamHandler import streamHandler
from lib.indexHandler import indexHandler
from lib.cameraController import cameraController

serverPort=8000

def cb(data):
    print (data)
    ret =  json.dumps(
        {
            "tick": time.time(),
            "data": data
        })
    asyncio.run(wsHandler.broadcast(ret))

#mpu6050Controller = mpu6050Controller(cb)
#mpu6050Controller.start()
#wsHandler.setmpu(mpu6050Controller)
wsHandler.setmpu(False)

cameraController = cameraController()
streamHandler.setStreamingOutput(cameraController.getOutputStream())

requestHandlers = [
    (r"/ws/", wsHandler),
    (r"/", indexHandler),
    (r"/index.html", indexHandler),
    (r'/js/(.*)', tornado.web.StaticFileHandler, {'path': 'www/js'}),
    (r'/css/(.*)', tornado.web.StaticFileHandler, {'path': 'www/css'}),
    (r'/images/(.*)', tornado.web.StaticFileHandler, {'path': 'www/images'}),
     (r"/stream.mjpg", streamHandler),
]

try:
    application = tornado.web.Application(requestHandlers)
    application.listen(serverPort)
    loop = tornado.ioloop.IOLoop.current()
    loop.start()
except KeyboardInterrupt:
    loop.stop()
finally:
    mpu6050Controller.terminate()
    camera.stop()

