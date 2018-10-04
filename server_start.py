from server.UdpServer import UdpServer


def test_menu(sv):
    op = 0
    while op != 6:
        op = int(input("----------------\n"
                       "[1] Print rooms\n"
                       "Choose: "))
        if op == 1:
            print(sv.rooms)


server = UdpServer()
server.start()
test_menu(server)