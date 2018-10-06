from threading import Thread
import json


class CommandHandler(Thread):
    def __init__(self, client_handler, command):
        super(CommandHandler, self).__init__(name='Command Handler')
        self.command = command
        self.setDaemon(True)
        self.client_handler = client_handler

    def run(self):
        if self.command:
            decoded = self.command.decode('utf-8')
            try:
                data = json.loads(decoded)
            except ValueError as err:
                print(err)
                raise ValueError('Expecting a JSON string from client, but got something else:', decoded)
            if data is not None:
                try:
                    if data['client_uid'] == self.client_handler.uidHex:
                        payload_keys = data['payload'].keys()
                        action = data['action']
                        if action == 'join_room':
                            self.client_handler.handle_cmd_join_room(data, payload_keys)
                        if action == 'leave_room':
                            self.client_handler.handle_cmd_leave_room()
                        if action == 'toggle_ready':
                            self.client_handler.handle_cmd_toggle_ready()
                        if action == 'player_shoot':
                            self.client_handler.handle_cmd_player_shoot(data, payload_keys)
                        if action == 'ping':
                            pass
                except KeyError:
                    pass