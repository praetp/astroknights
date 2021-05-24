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
import time
import math


serverPort=8002

interests=['shutter_speed','brightness','awb_mode','exposure_speed','awb_gains','crop','analog_gain','framerate']
#interests=['analog_gain']

def dump(obj):
  for attr in dir(obj):
    if attr in interests:
        try:
            print("obj.%s = %r" % (attr, getattr(obj, attr)))
        except:
            print("obj.%s = unreadable" % (attr))
     
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
            n = str(now)
            print(n)
            camera.annotate_text=n
        return self.buffer.write(buf)
    
    def flush(self):
        print("Flush")

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
    (r"/stream.mjpg", streamHandler),
]

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
        application = tornado.web.Application(requestHandlers)
        application.listen(serverPort)
        loop = tornado.ioloop.IOLoop.current()
        loop.start()
    except KeyboardInterrupt:
        camera.stop_recording()
        camera.close()
        loop.stop()
    finally:
        camera.stop_recording()

