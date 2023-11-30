# Terrible, bad, shit
# + Don't use
# + Rewrite in go

import threading
import socket
import paramiko

class SSHServer(paramiko.ServerInterface):
    def __init__(self):
        self.event = threading.Event()

    def check_auth_password(self, username, password):
        print(f'Tried login with {username}:{password}')
        return paramiko.AUTH_FAILED

    def check_auth_publickey(self, username, key):
        print(f'Tried login in with {username}:{key.hex()}')
        return paramiko.AUTH_FAILED

    def get_allowed_auths(self, username):
        return 'publickey'

    def check_channel_exec_request(self, channel, command):
        channel.send(command)
        channel.send_exit_status(0)
        return True

class SSHThread(threading.Thread):
    def __init__(self, client, addr, server):
        threading.Thread.__init__(self)
        self.client = client
        self.addr = addr
        self.server = server

    def run(self):
        transport = paramiko.Transport(self.client)
        transport.add_server_key(paramiko.RSAKey.generate(2048))
        transport.start_server(server=self.server)
        channel = transport.accept(20)
        if channel is None:
            transport.close()
            return
        channel.send('Welcome to my SSH server!\n')
        while True:
            try:
                command = channel.recv(1024)
                if not command:
                    break
                self.server.check_channel_exec_request(channel, command.decode())
            except Exception as e:
                print(f'Connection closed')
        channel.close()
        transport.close()

if __name__ == '__main__':
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(('0.0.0.0', 2222))
    server_socket.listen(100)
    server = SSHServer()
    while True:
        try:
            client, addr = server_socket.accept()
            ssh_thread = SSHThread(client, addr, server)
            ssh_thread.start()
        except Exception:
            pass
