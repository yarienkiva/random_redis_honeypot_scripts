#!/usr/bin/env python3

from pwn import *
context.log_level = 'DEBUG'

r = remote('localhost', 9001)

r.sendline(b'PING')
r.recvline() # +PONG

r.sendline(b'REPLCONF capa eof capa psync2')
r.recvline() # +OK

r.sendline('PSYNC c9392b988c38b2f3ea97fe1843ae4325688cc993 1')
r.recvline() # +FULLRESYNC d1b852c852c4a8b33009131295361daee624bdb8 0

n = r.recvline() # $175

n = int(n.strip(b'$'))

with open('/tmp/dump', 'wb') as f:
	f.write(r.recv(n))
