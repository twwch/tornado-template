from argparse import ArgumentParser
from tornado.web import Application
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
from config.env import env
from handler.state import StateHandler

routes = [
    (r"/api/state", StateHandler),

]

if __name__ == "__main__":

    parser = ArgumentParser()
    parser.add_argument("--port", default=9897, type=int, help="listen port")
    parser.add_argument(
        "--numprocs", default=8, type=int, help="number of sub-process to fork"
    )
    options, _ = parser.parse_known_args()
    app = Application(routes, **env["tornado"], cookie_secret="x1i2a3o4d5u6o7", serve_traceback=True)
    server = HTTPServer(app, xheaders=True)

    port = options.port or env["port"]
    num_procs = options.numprocs or env["numprocs"]

    if env["tornado"]["debug"]:
        print('server.listen({})'.format(port))
        server.listen(port)
    else:
        server.bind(port)
        server.start(num_procs)
    IOLoop.current().start()
