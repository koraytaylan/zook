from zook import *
import tornado.ioloop
import tornado.httpserver
import tornado.autoreload


def main():
    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(8080)
    ioloop = tornado.ioloop.IOLoop.instance()
    #tornado.autoreload.start(ioloop, 100)
    ioloop.start()


if __name__ == "__main__":
    main()