import io
import picamera
from threading import Condition
from fractions import Fraction
import tornado
import datetime

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
        return self.buffer.write(buf)

    def flush(self):
        print("Flush")

class cameraController():

    def annotate(self):
        #dump(self.camera)
        n = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(n)
        self.camera.annotate_text = n

    def __init__(self):
        print("cameraController: INIT")
        self.camera = picamera.PiCamera(sensor_mode=1, resolution='1920x1080' ,framerate=Fraction(1, 1))
        self.output = StreamingOutput()
        #self.camera.rotation = 90
        #self.camera.framerate = 2
        self.camera.shutter_speed = 1000000
        self.camera.iso = 1600
        #camera.crop = (0.2, 0.2, 0.6, 0.6)
        self.camera.awb_mode = 'off'
        self.camera.awb_gains = Fraction(329, 256)
        self.camera.brightness = 60
        self.camera.exposure_mode="off"
        self.camera.start_recording(self.output, format='mjpeg')
        self.timestamploop = tornado.ioloop.PeriodicCallback(self.annotate, 1000);
        self.timestamploop.start()


    def getOutputStream(self):
        return self.output

    def stop(self):
        timestamploop.stop()
        self.camera.stop_recording()
