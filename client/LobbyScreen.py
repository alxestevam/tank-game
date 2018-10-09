import tkinter as tk
import client.CONFIG as CONFIG
from threading import Thread


class LobbyScreen(Thread):
    def __init__(self, server_handler):
        super(LobbyScreen, self).__init__(name="Lobby Screen Thread")
        self.serverHandler = server_handler
        self.setDaemon(True)
        self.win = None
        self.status_text = None

    def run(self):
        self.win = tk.Tk()
        self.win.title("Lobby")
        self.win.geometry("300x150")
        self.status_text = tk.StringVar()

        lb_status = tk.Label(textvariable=self.status_text)
        lb_is_ready = tk.Label()

        btn_status = tk.Button(text="Status", width=20, command=self.get_client_status)
        btn_join_room = tk.Button(text="Join Room", width=20)
        btn_leave_room = tk.Button(text="Leave Room", width=20, command=self.serverHandler.cmd_leave_room)
        btn_toggle_ready = tk.Button(text="Ready", width=20, command=self.serverHandler.cmd_toggle_ready)

        lb_status.grid(row=0, column=0)
        lb_is_ready.grid(row=0, column=1)
        btn_join_room.grid(row=1, columnspan=2)
        btn_leave_room.grid(row=2, columnspan=2)
        btn_toggle_ready.grid(row=3, columnspan=2)
        btn_status.grid(row=4, columnspan=2)

        self.win.mainloop()

    def get_client_status(self):
        if self.serverHandler.ready:
            self.status_text.set("Ready")
        else:
            self.status_text.set("Not ready!")


if __name__ == '__main__':
    lobby = LobbyScreen(None)
    lobby.start()
    lobby.join()
