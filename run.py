import argparse
from http.server import ThreadingHTTPServer
from app.controllers.http import make_handler

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', type=int, default=8002)
    parser.add_argument('--host', default='127.0.0.1')
    args = parser.parse_args()
    server = ThreadingHTTPServer((args.host,args.port),make_handler())
    print(f'Demo local: http://{args.host}:{args.port}', flush=True)
    try: server.serve_forever()
    except KeyboardInterrupt: server.server_close()
