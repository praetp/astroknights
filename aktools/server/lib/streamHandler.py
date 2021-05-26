import tornado
import logging

class streamHandler(tornado.web.RequestHandler):

    output = False

    @classmethod
    def setStreamingOutput(cls, output):
        cls.output = output

    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self):
        ioloop = tornado.ioloop.IOLoop.current()

        self.set_header('Cache-Control', 'no-store, no-cache, must-revalidate, pre-check=0, post-check=0, max-age=0')
        self.set_header('Pragma', 'no-cache')
        self.set_header('Content-Type', 'multipart/x-mixed-replace;boundary=--jpgboundary')
        self.set_header('Connection', 'close')
        try:
            while True:
                with self.output.condition:
                    self.output.condition.wait()
                    frame = self.output.frame
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