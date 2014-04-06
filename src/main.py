from zook import *
import tornado.ioloop
import tornado.httpserver
import sys
import os


def main(argv):
    public_path = 'app'
    if len(argv) > 0 and argv[0] == 'dist':
        public_path = 'dist'
    public_path = os.path.join(
        os.path.dirname(
            os.path.realpath(__file__)
            ),
        os.path.pardir,
        public_path
        )
    app = Application(public_path)
    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(8080)
    ioloop = tornado.ioloop.IOLoop.instance()
    ioloop.start()


if __name__ == "__main__":
    main(sys.argv[1:])