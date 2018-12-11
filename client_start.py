from client.ServerHandler import ServerHandler

ip = input('IP: (Default = 127.0.0.1)')
port = input('Port: (Default = 10939)')

if ip == '':
    ip = '127.0.0.1'
if port == '':
    port = 10939

nickname = input('Nickname: ')

client = ServerHandler((ip, port), nickname)
client.start()
client.test_menu()
client.join()

