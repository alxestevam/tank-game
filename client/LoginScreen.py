import tkinter as tk


class LoginScreen:
    def __init__(self):
        self.win = tk.Tk()
        self.win.title("Login")
        self.win.geometry("300x150")

        lb_login = tk.Label(text="Login: ")
        lb_password = tk.Label(text="Password: ")

        entry_login = tk.Entry()
        entry_password = tk.Entry()

        btn_login = tk.Button(text="Login", width=20)

        lb_login.grid(row=0, column=0)
        lb_password.grid(row=1, column=0)
        entry_login.grid(row=0, column=1)
        entry_password.grid(row=1, column=1)
        btn_login.grid(row=2, columnspan=2)


if __name__ == '__main__':
    screen = LoginScreen()
    screen.win.mainloop()
