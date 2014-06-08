from zook import *
import tornado.ioloop
import tornado.httpserver
import sys
import os


def main(argv):
    port = 8080
    public_path = 'app'
    if len(argv) > 0 and argv[0] == 'dist':
        port = 80
        public_path = 'dist'
    data_path = 'data'
    public_path = os.path.join(
        os.path.dirname(
            os.path.realpath(__file__)
            ),
        public_path
        )
    data_path = os.path.join(
        os.path.dirname(
            os.path.realpath(__file__)
            ),
        data_path
        )
    app = Application(public_path, data_path)
    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(port)
    ioloop = tornado.ioloop.IOLoop.instance()
    ioloop.start()


if __name__ == "__main__":
    argv = None
    if len(sys.argv) > 0:
        argv = sys.argv[1:]
    main(argv)