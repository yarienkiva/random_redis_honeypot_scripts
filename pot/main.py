import docker

import threading
import logging
import socket
import select
import time
import sys

class Server:
    def __init__(self, image, bind_port, service_port):
        self.IMAGE     = image
        self.BIND_PORT = bind_port
        self.SERV_PORT = service_port

        self.BUFFER_SIZE    = 2 ** 20
        self.THREAD_TIMEOUT = 60 * 60 * 24

        self.containers = {}
        self.port_map   = {}

        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.s.bind(('', self.BIND_PORT))
        self.s.listen(1)

    def loop_forever(self):
        while True:
            s_src, a_src = self.s.accept()

            if a_src[0] not in self.containers:
                logging.info(f'\x1b[32m{a_src[0]}:{a_src[1]} >con (new)\x1b[0m')

                self.port_map[a_src[0]] = self.get_free_port()
                self.containers[a_src[0]] = client.containers.run(self.IMAGE,
                                                detach=True,
                                                name=f'{self.IMAGE.replace(":","_")}_{a_src[0]}',
                                                ports={self.SERV_PORT: self.port_map[a_src[0]]})
            else:
                logging.info(f'\x1b[32m{a_src[0]}:{a_src[1]} >con\x1b[0m')

            while self.containers[a_src[0]].status != 'running':
                self.containers[a_src[0]].reload()
                time.sleep(1)

            new_host = ('localhost', self.port_map[a_src[0]])

            d = threading.Thread(target=self.proxy_thread, args=(s_src, a_src, new_host))
            d.setDaemon(True)
            d.start()

    def proxy_thread(self, s_src, a_src, new_host):
        s_dst = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s_dst.connect(new_host)

        def done(e):
            logging.info(f'\x1b[34m{a_src[0]}:{a_src[1]} <dis ({e})\x1b[0m')
            s_src.close()
            s_dst.close()

        while True:
            s_read, _, _ = select.select([s_src, s_dst], [], [], self.THREAD_TIMEOUT)

            if not s_read:
                return done('nothing to read')

            for s in s_read:
                try:
                    data = s.recv(self.BUFFER_SIZE)
                    assert len(data), 'data len = 0'
                except Exception as e:
                    return done(e)

                if s == s_src:
                    logging.info(f'\x1b[32m{a_src[0]}:{a_src[1]} ->\x1b[0m {data}')
                    s_dst.sendall(data)

                elif s == s_dst:
                    logging.debug(f'\x1b[34m{a_src[0]}:{a_src[1]} <-\x1b[0m {data[:200]}')
                    s_src.sendall(data)

    def get_free_port(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind(('', 0))
        _, port = sock.getsockname()
        sock.close()
        return port

logging.basicConfig(level=logging.INFO)

print('Starting dispatcher')

logging.debug('Starting docker...')
client = docker.from_env()

for c in client.containers.list(all=True):
    print('Killing', c)
    try:    c.kill()
    except: pass
    try:    c.remove()
    except: pass

print('Starting dispatcher, looping...')
server = Server('redis:5.0.5', bind_port=6379, service_port=6379)
#server = Server('nginx:latest', bind_port=8080, service_port=80)
server.loop_forever()
