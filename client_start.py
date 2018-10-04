from client.ServerHandler import ServerHandler


def test_menu(server_handler):
    op = 0
    while op != 7:
        op = int(input("----------------------------\n"
                       "[1] Print Current Room uid\n"
                       "[2] Print Main Room Uid\n"
                       "[3] Join room\n"
                       "[4] Leave room\n"
                       "[5] Ready\n"
                       "[6] Status\n"
                       "[7] Disconnect\n"
                       "Choose: "))
        if op == 1:
            print(server_handler.currentRoomUid)
        elif op == 2:
            print(server_handler.mainRoomUid)
        elif op == 3:
            room_uid = input("UID: ")
            server_handler.cmd_join_room(room_uid)
        elif op == 4:
            server_handler.cmd_leave_room()
        elif op == 5:
            server_handler.cmd_toggle_ready()
        elif op == 6:
            if server_handler.ready:
                print('Ready!')
            else:
                print('Not ready.')


client = ServerHandler(('127.0.0.1', 10939))
client.start()
test_menu(client)
