import docker

import threading
import logging
import socket
import select
import time
import sys
import os

class Server:
	def __init__(self, image, bind_port):
		self.IMAGE     = image
		self.BIND_PORT = bind_port
		self.SOCK_DIR  = os.getcwd() + '/sock_drawer/'

		self.BUFFER_SIZE    = 2 ** 20
		self.THREAD_TIMEOUT = 60 * 60 * 24

		self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.s.bind(('', self.BIND_PORT))
		self.s.listen(1)

	def loop_forever(self):
		while True:
			s_src, (a_host, a_port) = self.s.accept()

			if f'{a_host}.sock' not in os.listdir(self.SOCK_DIR):
				logging.info(f'{a_host}:{a_port} > new!')

				cont = client.containers.run(self.IMAGE,
							detach=True,
							name=f'{self.IMAGE.replace(":","_")}_{a_host}',
							volumes={f'{self.SOCK_DIR}{a_host}.sock': {
										'bind': '/redis.sock',
										'mode': 'rw'}},
							cpu_period=100000,
							cpu_quota=10000)

				while cont.status != 'running':
					cont.reload()
					time.sleep(1)

			s_dst = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
			s_dst.bind(f'{self.SOCK_DIR}{a_host}.sock')
			s_dst.listen(1)
			logging.info(f'{a_host}:{a_port} >con')

			d = threading.Thread(target=self.proxy_thread, args=(s_src, (a_host, a_port), s_dst))
			d.setDaemon(True)
			d.start()

	def proxy_thread(self, s_src, a_src, s_dst):

		def done(e):
			logging.info(f'{a_src[0]}:{a_src[1]} <dis ({e})')
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
					logging.info(f'{a_src[0]}:{a_src[1]} -> {data}')
					s_dst.sendall(data)

				elif s == s_dst:
					logging.debug(f'{a_src[0]}:{a_src[1]} <- {data[:200]}')
					s_src.sendall(data)

logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)

logging.info('Starting dispatcher')
logging.debug('Starting docker...')
client = docker.from_env()

for c in client.containers.list(all=True):
	logging.debug('Killing', c)
	try:    c.kill()
	except: pass
	try:    c.remove()
	except: pass

logging.info('Starting dispatcher, looping...')
server = Server('redpot:v5', bind_port=6379)
server.loop_forever()
