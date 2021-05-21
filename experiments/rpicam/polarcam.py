import io
import picamera
import logging
import socketserver
import time
import datetime
from fractions import Fraction
from threading import Condition
from http import server
from pprint import pprint


PAGE="""\
<html>
<head>
<title>Raspberry Pi - Polar Cam</title>
</head>
<body>
<div style="display:flex; flex-wrap:wrap">
<img src="stream.mjpg" width="auto" height="100%">
</div>
</body>
</html>
"""

#<center><img src="stream.mjpg" width="1296" height="730"></center>
camera_main = 0

interests=['shutter_speed','brightness','awb_mode','exposure_speed','awb_gains','crop','analog_gain']

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
        now = datetime.datetime.now()
        print(str(now))
        dump(camera_main)
        camera_main.annotate_text=str(now)
        if buf.startswith(b'\xff\xd8'):
            # New frame, copy the existing buffer's content and notify all
            # clients it's available
            self.buffer.truncate()
            with self.condition:
                self.frame = self.buffer.getvalue()
                self.condition.notify_all()
            self.buffer.seek(0)
        return self.buffer.write(buf)

class StreamingHandler(server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(301)
            self.send_header('Location', '/index.html')
            self.end_headers()
        elif self.path == '/index.html':
            content = PAGE.encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.send_header('Content-Length', len(content))
            self.end_headers()
            self.wfile.write(content)
        elif self.path == '/stream.mjpg':
            self.send_response(200)
            self.send_header('Age', 0)
            self.send_header('Cache-Control', 'no-cache, private')
            self.send_header('Pragma', 'no-cache')
            self.send_header('Content-Type', 'multipart/x-mixed-replace; boundary=FRAME')
            self.end_headers()
            try:
                while True:
                    with output.condition:
                        output.condition.wait()
                        frame = output.frame
                    self.wfile.write(b'--FRAME\r\n')
                    self.send_header('Content-Type', 'image/jpeg')
                    self.send_header('Content-Length', len(frame))
                    self.end_headers()
                    self.wfile.write(frame)
                    self.wfile.write(b'\r\n')
            except Exception as e:
                logging.warning(
                    'Removed streaming client %s: %s',
                    self.client_address, str(e))
        else:
            self.send_error(404)
            self.end_headers()

class StreamingServer(socketserver.ThreadingMixIn, server.HTTPServer):
    allow_reuse_address = True
    daemon_threads = True



with picamera.PiCamera(resolution='2592x1944' ,framerate=Fraction(1, 1)) as camera:
    output = StreamingOutput()
    #Uncomment the next line to change your Pi's Camera rotation (in degrees)
    #camera.rotation = 90
    #camera.framerate = 2
    camera.shutter_speed = 1000000
    camera.iso = 1600
    camera.crop = (0.2, 0.2, 0.6, 0.6)
    camera.awb_mode = 'off'
    camera.awb_gains = Fraction(329, 256)
    camera.brightness = 60
    #camera.crop = 
    time.sleep(1)
    camera.exposure_mode="off"
    print(camera.shutter_speed)
    print(camera.exposure_speed)
    camera_main = camera

    camera.start_recording(output, format='mjpeg')
    try:
        address = ('', 8000)
        server = StreamingServer(address, StreamingHandler)
        server.serve_forever()
    finally:
        camera.stop_recording()
