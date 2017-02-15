from __future__ import print_function
import tornado.httpserver
import tornado.web
import tornado.websocket
import tornado.ioloop
import tornado.gen

import tornadoredis


c = tornadoredis.Client()
c.connect()


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("template.html", title="Optumsoft Assignment")


class tempHandler(tornado.web.RequestHandler):
    def post(self):
        message = self.get_argument('message')
        c.publish('test_channel', message)
        self.set_header('Content-Type', 'text/plain')
        self.write('sent: %s' % (message,))


class tempTracker(tornado.websocket.WebSocketHandler):
    def __init__(self, *args, **kwargs):
        super(tempTracker, self).__init__(*args, **kwargs)
        self.listen()

    @tornado.gen.engine
    def listen(self):
        self.client = tornadoredis.Client()
        self.client.connect()
        yield tornado.gen.Task(self.client.subscribe, 'test_channel')
        self.client.listen(self.on_message)

    def on_message(self, msg):
        if msg.kind == 'message':
            self.write_message(str(msg.body))
        if msg.kind == 'disconnect':
            # Do not try to reconnect, just send a message back
            # to the client and close the client connection
            self.write_message('The connection terminated '
                               'due to a Redis server error.')
            self.close()

    def on_close(self):
        if self.client.subscribed:
            self.client.unsubscribe('test_channel')
            self.client.disconnect()
    
    def check_origin(self, origin):
        return True        


application = tornado.web.Application([
    (r'/', MainHandler),
    (r'/addtemp', tempHandler),
    (r'/track', tempTracker),
])

if __name__ == '__main__':
    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(8888)
    print('Demo is runing at 0.0.0.0:8888\nQuit the demo with CONTROL-C')
    tornado.ioloop.IOLoop.instance().start()
