from threading import Thread
import math
import time
from mpu6050 import mpu6050

class mpu6050Controller(Thread):

    maxvals=10

    vals = {
        "rolloffset": 0,
        "ax": [],
        "ay": [],
        "az": [],
        "gx": [],
        "gy": [],
        "gz": [],
    }

    def sendUpdate(self):
        self.cb({
            "ax": self.getnum(self.vals["ax"]),
            "ay": self.getnum(self.vals["ay"]),
            "az": self.getnum(self.vals["az"]),
            "gx": self.getnum(self.vals["gx"]),
            "gy": self.getnum(self.vals["gy"]),
            "gz": self.getnum(self.vals["gz"]),
            "roll": self.roll(),
            "rolltomins": self.rolltominutes(),
            "rolltohours": self.rolltohours(),
            "rolloffset": self.vals["rolloffset"]
        })

    def __init__(self, cb):
        print("mpu6050Controller: INIT")
        super().__init__()
        self.sensor = mpu6050(0x68)
        self._running = True
        self.cb = cb

    def terminate(self):
        print("mpu6050Controller: TERM")
        self._running = False

    def addToArray(self, t, val):
        t.append(val)
        if (len(t) > self.maxvals):
            t.pop(0)

    def updateData(self):
        accelerometer_data = self.sensor.get_accel_data()
        gyro_data = self.sensor.get_gyro_data()
        self.addToArray(self.vals["ax"], accelerometer_data['x'] * 3.9)
        self.addToArray(self.vals["ay"], accelerometer_data['y'] * 3.9)
        self.addToArray(self.vals["az"], accelerometer_data['z'] * 3.9)

        self.addToArray(self.vals["gx"], gyro_data['x'])
        self.addToArray(self.vals["gy"], gyro_data['y'])
        self.addToArray(self.vals["gz"], gyro_data['z'])
#         self.addToArray(self.vals["ax"], 1)
#         self.addToArray(self.vals["ay"], 2)
#         self.addToArray(self.vals["az"], 3)
#         self.addToArray(self.vals["gx"], 4)
#         self.addToArray(self.vals["gy"], 5)
#         self.addToArray(self.vals["gz"], 6)

    def getnum(self, t):
        if (len(t) > 0):
            return round(sum(t) / len(t), 2)
        else:
            return 0

    def getval(self, t):
        return str(self.getnum(t))

    def printData(self):
        print("AX: {} AY: {} AZ: {} GX: {} GY: {} GZ: {} ROLL:{} ROLLM:{} ROLLH:{}".format(
            self.getval(self.vals["ax"]),
            self.getval(self.vals["ay"]),
            self.getval(self.vals["az"]),
            self.getval(self.vals["gx"]),
            self.getval(self.vals["gy"]),
            self.getval(self.vals["gz"]),
            self.roll(),
            self.rolltominutes(),
            self.rolltohours()))

    def roll(self):
        return round(math.atan2(self.getnum(self.vals["ay"]), self.getnum(self.vals["az"])) * 180 / math.pi - self.vals["rolloffset"], 2)

    def rolltominutes(self):
        #return int(roll() + 180) * 1440 / 360
        r = self.roll()
        if r > 0:
            res = int(- (r * 1440 / 360))
            res = 360 - res
        else:
            #return int(360 + r * 1440 / 360)
            res = int(- r * 1440 / 360)
            res = 360 - res
        if (res > 1440):
            res -= 1440
        if (res < 0):
            res += 1440
        return res

    def rolltohours(self):
        r = self.rolltominutes()
        h = int(r / 60)
        m = int(r % 60)
        s = int(r % 3600)
        return str("%d:%02d:%02d" % (h,m,s))

    def calibrate(self):
        self.vals["rolloffset"]+=self.roll()

    def run(self):
        print("mpu6050Controller: RUN")
        ctr = 0
        while self._running:
            ctr+=1
#             print("mpu6050Controller: Running")
            self.updateData()
#             self.printData()
            time.sleep(0.1)
            if (ctr > 10):
                self.sendUpdate()
                ctr=0

            




