# Web streaming example
# Source code from the official PiCamera package
# http://picamera.readthedocs.io/en/latest/recipes2.html#web-streaming

import io
import picamera
import logging
import socketserver
import time
import datetime
from string import Template
from fractions import Fraction
from threading import Condition
from http import server
import tornado.web, tornado.ioloop, tornado.websocket , tornado 
import io, os, socket
from mpu6050 import mpu6050
import time
import math


PAGE="""\
<html>
<head>
<title>Raspberry Pi - Polar and Angle</title>
</head>
<body>
<div style="display:flex; flex-wrap:wrap">
<img src="stream.mjpg" width="auto" height="100%">
<script>
	window.onload = function(){	
		var ws = new WebSocket("ws://$ip:$port/ws/");
		ws.binaryType = 'arraybuffer';
		ws.addEventListener('message',function(event){
                        console.log(event)
		});
	}     
</script>
</div>
</body>
</html>
"""

sensor = mpu6050(0x68)

ax = []
ay = []
az = []
gx = []
gy = []
gz = []

def getnum(t):
    if (len(t) > 0):
        return round(sum(t) / len(t), 2)
    else:
        return 0

def getval(t):
    return str(getnum(t))

maxvals=10
def add(t, val):
    t.append(val)
    if (len(t) > maxvals):
        t.pop(0)

def roll():
    return round(math.atan2(getnum(ay), getnum(az)) * 180 / math.pi, 2)

def rolltominutes():
    #return int(roll() + 180) * 1440 / 360
    r = roll()
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

def rolltohours():
    r = rolltominutes()
    h = int(r / 60)
    m = int(r % 60)
    s = int(r % 3600)
    return str("%d:%02d:%02d" % (h,m,s))

serverPort=8000
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.connect(('8.8.8.8', 0))
serverIp = s.getsockname()[0]

#<center><img src="stream.mjpg" width="1296" height="730"></center>

interests=['shutter_speed','brightness','awb_mode','exposure_speed','awb_gains','crop','analog_gain','framerate']
#interests=['analog_gain']


def dump(obj):
  for attr in dir(obj):
    if attr in interests:
        try:
            print("obj.%s = %r" % (attr, getattr(obj, attr)))
        except:
            print("obj.%s = unreadable" % (attr))
     
class wsHandler(tornado.websocket.WebSocketHandler):
    connections = []

    def check_origin(self, origin):
        return True

    def open(self):
        self.connections.append(self)

    def on_close(self):
        self.connections.remove(self)

    def on_message(self, message):
        pass

    @classmethod
    def hasConnections(cl):
        if len(cl.connections) == 0:
            return False
        return True

    @classmethod
    async def broadcast(cl, message):
        for connection in cl.connections:
            try:
                await connection.write_message(message, True)
            except tornado.websocket.WebSocketClosedError:
                pass
            except tornado.iostream.StreamClosedError:
                pass

class StreamingOutput(object):
    def __init__(self):
        self.frame = None
        self.buffer = io.BytesIO()
        self.condition = Condition()

    def write(self, buf):
        if buf.startswith(b'\xff\xd8'):
            # New frame, copy the existing buffer's content and notify all
            # clients it's available
            self.buffer.truncate()
            with self.condition:
                self.frame = self.buffer.getvalue()
                self.condition.notify_all()
            self.buffer.seek(0)
            now = datetime.datetime.now()
            #dump(camera)
            r = str(roll())
            m = str(rolltominutes())
            h = str(rolltohours())
            n = str(now)
            print(n + " : " + r + " : " + m + " : " + h)
            camera.annotate_text=n + " | ROLL: " + r + "degrees | HRS: " + h
        return self.buffer.write(buf)
    
    def flush(self):
        print("Flush")


class indexHandler(tornado.web.RequestHandler):
    def get(self):
        content = PAGE.encode('utf-8')
        self.write(templatize(PAGE, {'ip':serverIp, 'port':serverPort}))

def templatize(content, replacements):
    tmpl = Template(content)
    return tmpl.substitute(replacements)

class streamHandler(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self):
        ioloop = tornado.ioloop.IOLoop.current()

        self.set_header('Cache-Control', 'no-store, no-cache, must-revalidate, pre-check=0, post-check=0, max-age=0')
        self.set_header( 'Pragma', 'no-cache')
        self.set_header( 'Content-Type', 'multipart/x-mixed-replace;boundary=--jpgboundary')
        self.set_header('Connection', 'close')
        try:
            while True:
                with output.condition:
                    output.condition.wait()
                    frame = output.frame
                print("New Frame: ")
                self.write('--jpgboundary')
                self.write('Content-Type: image/jpeg\r\n')
                self.write('Content-Length: %s\r\n\r\n' % len(frame))
                self.write(frame)
                yield tornado.gen.Task(self.flush)
        except Exception as e:
            logging.warning(
                'Removed streaming client %s: %s',
                self.client_address, str(e))

class StreamingServer(socketserver.ThreadingMixIn, server.HTTPServer):
    allow_reuse_address = True
    daemon_threads = True


requestHandlers = [
    (r"/ws/", wsHandler),
    (r"/", indexHandler),
    (r"/index.html", indexHandler),
    (r"/stream.mjpg", streamHandler),
]

def getData():
    accelerometer_data = sensor.get_accel_data()
    gyro_data = sensor.get_gyro_data()
    add(ax, accelerometer_data['x'] * 3.9)
    add(ay, accelerometer_data['y'] * 3.9)
    add(az, accelerometer_data['z'] * 3.9)

    add(gx, gyro_data['x'])
    add(gy, gyro_data['y'])
    add(gz, gyro_data['z'])
#    if wsHandler.hasConnections():
#        loop.add_callback(callback=wsHandler.broadcast, message=roll())

#with picamera.PiCamera(resolution='2592x1944' ,framerate=Fraction(1, 2)) as camera:
#with picamera.PiCamera(resolution='1024x768' ,framerate=Fraction(1, 1)) as camera:
with picamera.PiCamera(sensor_mode=1, resolution='1920x1080' ,framerate=Fraction(1, 1)) as camera:
    output = StreamingOutput()
    #Uncomment the next line to change your Pi's Camera rotation (in degrees)
    #camera.rotation = 90
    #camera.framerate = 2
    camera.shutter_speed = 1000000
    camera.iso = 1600
    #camera.crop = (0.2, 0.2, 0.6, 0.6)
    camera.awb_mode = 'off'
    camera.awb_gains = Fraction(329, 256)
    camera.brightness = 50
    #camera.crop = 
    time.sleep(1)
    camera.exposure_mode="off"

    camera.start_recording(output, format='mjpeg')
    try:
        data = tornado.ioloop.PeriodicCallback(getData, 100);
        application = tornado.web.Application(requestHandlers)
        application.listen(serverPort)
        loop = tornado.ioloop.IOLoop.current()
        data.start()
        loop.start()
    except KeyboardInterrupt:
        camera.stop_recording()
        camera.close()
        loop.stop()
        data.stop()
    finally:
        camera.stop_recording()

#while True:
#    cnt+=1
#    if (cntrstrt >= 0):
#        cntrstrt += 1
#    accelerometer_data = sensor.get_accel_data()
#    gyro_data = sensor.get_gyro_data()
#


#    add(ax, accelerometer_data['x'] * 3.9)
#    add(ay, accelerometer_data['y'] * 3.9)
#    add(az, accelerometer_data['z'] * 3.9)

#    add(gx, gyro_data['x'])
#    add(gy, gyro_data['y'])
#    add(gz, gyro_data['z'])


#    time.sleep (0.2)
#    if (cnt == 1):
#        prnt()
#    if (cnt >= prt):
#        cnt=0

#    if (cntrstrt > 20):
#        print("BASELINE")
#        baseroll1=roll1()
#        baseroll2=roll2()
#        baseroll3=roll3()
#        baseroll4=roll4()
#        baseroll5=roll5()
#        baseroll6=roll6()
#        baseanotherpitch=anotherpitch()
#        baseanotherroll=anotherroll()
#        baseanotheryaw=anotheryaw()
#        bpitch=pitch()
#        broll=roll()
#        cntrstrt=-1

