import os
import tornado.web, tornado

site_dir="www"

class indexHandler(tornado.web.RequestHandler):

    def getFile(self, filePath):
        file = open(filePath,'r')
        content = file.read()
        file.close()
        return content

    def get(self):
        self.write(self.getFile(site_dir + "/index.html"))