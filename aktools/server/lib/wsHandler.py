import tornado.web, tornado.ioloop, tornado.websocket , tornado
import io, os, socket
from lib.mpu6050Controller import mpu6050Controller

class wsHandler(tornado.websocket.WebSocketHandler):
    connections = []

    mpu6050Controller = False

    def check_origin(self, origin):
        return True

    def open(self):
        print ("OPEN WS")
        self.connections.append(self)


    def on_close(self):
        self.connections.remove(self)

    def on_message(self, message):
        print(message)
        if "calibrate" in message:
            print("CALIBRATE")
            self.mpu6050Controller.calibrate()
        if "reset" in message:
            print("RESET")
            self.mpu6050Controller.reset()

    @classmethod
    def setmpu(cls, mpu):
        cls.mpu6050Controller = mpu

    @classmethod
    def hasConnections(cl):
        if len(cl.connections) == 0:
            return False
        return True

    @classmethod
    async def broadcast(cl, message):
        for connection in cl.connections:
            try:
                await connection.write_message(message, False)
            except tornado.websocket.WebSocketClosedError:
                pass
            except tornado.iostream.StreamClosedError:
                pass
