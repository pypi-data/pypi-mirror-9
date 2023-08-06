import sys

from routes_demo.rest_server.router import APIRouter

from wsgiref.simple_server import make_server

from oslo.config import cfg


def main():
    
#     config.init(sys.argv[1:])
    
    cfg.CONF(args=sys.argv[1:])
    
    router = APIRouter()
    httpd = make_server('0.0.0.0', 9999, router)
    httpd.serve_forever()

if __name__ == "__main__":
    main()
