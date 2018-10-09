from client.ServerHandler import ServerHandler
from client.LoginScreen import LoginScreen
from client.LobbyScreen import LobbyScreen

ip = input('IP: (Default = 127.0.0.1)')
port = input('Port: (Default = 10939)')

if ip == '':
    ip = '127.0.0.1'
if port == '':
    port = 10939

client = ServerHandler((ip, port))
client.start()
client.join()
