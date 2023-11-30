from serializer import deserialize, is_serialized, token

import threading
import socket
import select
import sys

def INTERCEPTOR(d: bytes) -> bytes:

	OK = b"$3\r\n+OK\r\n"

	d = deserialize(d) if is_serialized(d) else token(d)
	print(d)

	tmp = [*map(bytes.lower, d)]

	if tmp[0] == b'eval':
		return OK

	if tmp[0] == b'module' and tmp[1] in [b'load', b'unload']:
		return OK

	if tmp[0] == b'slaveof' or tmp[0] == b'replicaof':
		return OK

	if tmp[0] == b'config' and tmp[1] == b'set':
		return OK

	return None

"""
*1$4PING
*3$8REPLCONF$14listening-port$46379
*5$8REPLCONF$4capa$3eof$4capa$6psync2
*3$5PSYNC$40d1b852c852c4a8b33009131295361daee624bdb8$215
"""

class Server:
	def __init__(self):
		self.BUFFER_SIZE    = 2 ** 20
		self.THREAD_TIMEOUT = 60 * 60 * 24
		self.REDIS_HOST     = ('localhost', 9001)

		self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.s.bind(('', 6379))
		self.s.listen(1)

	def loop_forever(self):
		while True:
			s_src, a_src = self.s.accept()
			print(f'{a_src[0]}:{a_src[1]} >con')

			d = threading.Thread(target=self.proxy_thread, args=(s_src, a_src))
			d.setDaemon(True)
			d.start()

		self.s.close()

	def proxy_thread(self, s_src, a_src):
		s_dst = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		s_dst.connect(self.REDIS_HOST)

		def done():
			print(f'{a_src[0]}:{a_src[1]} <dis')
			s_src.close()
			s_dst.close()

		while True:
			s_read, _, _ = select.select([s_src, s_dst], [], [], self.THREAD_TIMEOUT)

			if not s_read:
				return done()

			for s in s_read:
				try:
					data = s.recv(self.BUFFER_SIZE)
					assert len(data)
				except Exception:
					return done()

				if s == s_src:

					if is_serialized(data):
						arr = [data]
					else:
						arr = [d for d in data.split(b'\r\n') if d]

					for data in arr:
						print(f'{a_src[0]}:{a_src[1]} ->', end=' ')

						if d := INTERCEPTOR(data):
							s_src.sendall(d)
						else:
							s_dst.sendall(data)

				elif s == s_dst:
					s_src.sendall(data)

print('Started server, looping...')
server = Server()
server.loop_forever()