import threading
import socket
import json
from server.Constants import Constants


class ClientHandler(threading.Thread, socket.socket):
    def __init__(self, udp_server, uid, client_address, port, client_info):
        threading.Thread.__init__(self, name='Client Handler Thread')
        socket.socket.__init__(self, type=socket.SOCK_DGRAM)
        self.settimeout(2)
        self.bind(('', port))
        self.setDaemon(True)
        self.server = udp_server
        self.room = None
        self.clientAddress = client_address
        self.clientInfo = client_info
        self.ready = False
        self.match = None
        self.uid = uid

        self.send_uid_to_client()

    def run(self):
        while True:
            self.send_command()
            self.receive_command()

    def send_uid_to_client(self):
        print(self.uid)
        data = {'action': 'set_uid', 'payload': {'client_uid': str(self.uid)}}
        data = json.dumps(data)
        data = data.encode('utf-8')

        self.sendto(data, self.clientAddress)

    def send_command(self, cmd=None):
        pass

    def receive_command(self):
        data, address_info = self.recvfrom(Constants.BUFFER_SIZE)
        if data:
            decoded = data.decode('utf-8')
            try:
                data = json.loads(decoded)
            except ValueError as err:
                print(err)
                raise ValueError('Expecting a JSON string from client, but got something else:', decoded)
            if data is not None and isinstance(data, dict):
                if data['client_uid'] == self.uid:
                    if data['action'] == 'join_room':
                        self.server.player_join_room(data['payload'], self)

    def leave_room(self):
        pass

    def toggle_ready(self):
        self.ready = not self.ready
        self.room.ready_verifier()

        # Send success
        data = {'action': 'toggle_ready', 'payload': {'success': True}}
        data = json.dumps(data)
        data = data.encode('utf-8')

        self.send(data, self.clientAddress)

    def move_char(self):
        pass

    def shot(self, charge):
        pass
