import tkinter as tk
from tkinter import ttk
from tkinter import Menu
from tkinter import messagebox
from tkinter import StringVar, BooleanVar
from tkinter import filedialog as fd

from database import DB
from crypto import crypto_sys

from steam_connection import SteamAccount, SteamConnect

import logging

logger = logging.getLogger(__name__)


class SteamConnectionGui:

    def __init__(self, root: tk):
        try:
            self.steam_path = open('files/steam_path.txt', 'r').read()
        except FileNotFoundError:
            logger.debug("Path to steam not found!")
            self.steam_path = None

        try:
            self.sda_path = open('files/sda_path.txt', 'r').read()
        except FileNotFoundError:
            self.sda_path = None

        self.root = root
        self.root.geometry('250x250+600+300')
        self.root.resizable(False, False)
        self.root.title("Steam Authorized")
        self.root.protocol("WM_DELETE_WINDOW", self.close_system)
        self.root.bind('<Escape>', lambda e: self.root.destroy())
        self.new_window = None

        self.powered_label = ttk.Label(self.root, text="Powered by matsubus", font=('Consolas', 8, 'bold'))
        self.choose_label = ttk.Label(self.root, text="Choose Account", font=('Bahnschrift', 10, 'bold'))
        self.entry_button = ttk.Button(self.root, text="Enter Account",
                                       command=self.run_steam_connection)
        self.add_account_button = ttk.Button(self.root, text="Add Account",
                                             command=self.create_new_window)
        self.configure_button = ttk.Button(self.root, text="Configure Account",
                                           command=self.configure_accouns_window)

        self.combobox = ttk.Combobox(self.root, values=self.fetch_account_names(), state='readonly')

        if self.fetch_account_names():
            self.combobox.current(0)

    def draw_widgets(self):
        self.choose_label.place(relx=0.31, rely=0.2)
        self.powered_label.place(relx=0.03, rely=0.93)
        self.combobox.place(relx=0.22, rely=0.35)

        self.entry_button.place(relx=0.30, rely=0.55)
        self.add_account_button.place(relx=0.07, rely=0.7)
        self.configure_button.place(relx=0.5, rely=0.7)

    def draw_menu(self):
        menu_bar = Menu(self.root)

        file_menu = Menu(menu_bar, tearoff=0)
        file_menu.add_command(label='Выйти', command=self.close_system)
        menu_bar.add_cascade(label='File', menu=file_menu)

        func_menu = Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="Functions", menu=func_menu)

        edit_menu = Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="Settings", menu=edit_menu)
        edit_menu.add_command(label="Path to Steam", command=self.get_steam_path)
        edit_menu.add_command(label="Path to SDA", command=self.get_sda_path)

        self.root.configure(menu=menu_bar)

    def get_steam_path(self):
        filedialog = fd.askopenfilename()
        if filedialog:
            self.steam_path = str(filedialog)
            print(self.steam_path)
            with open('files/steam_path.txt', 'w') as f:
                f.write(r''.join(self.steam_path))

    def get_sda_path(self):
        filedialog = fd.askopenfilename()
        if filedialog:
            self.sda_path = str(filedialog)
            with open('files/sda_path.txt', 'w') as f:
                f.write(r''.join(self.sda_path))

    def create_new_window(self):
        self.new_window = NewAccountWindow(main_window)

    def get_data_from_child(self, child_window):
        account_name = child_window.name_entry.get()
        account_password = child_window.password_entry.get()
        sda_checkbox = child_window.SDA_var.get()
        print(sda_checkbox)
        child_window.root.destroy()

        DB.add_account(account_name, account_password, sda_checkbox)

        self.combobox = ttk.Combobox(self.root, values=self.fetch_account_names(), state='readonly')
        self.draw_widgets()

    @staticmethod
    def fetch_account_names():
        data = DB.fetch_data()
        data = [str(i[0]) for i in data]

        return data

    def run_steam_connection(self):
        password = self.get_password()
        sda = self.get_sda()
        steam_acc = SteamAccount(self.combobox.get(), password, sda)
        st_connection = SteamConnect(self.steam_path, self.sda_path, steam_account=steam_acc)
        st_connection.start()

    def configure_accouns_window(self):
        self.new_window = ConfigureAccountsWindow(main_window, self.combobox.get())

    def get_password(self):
        print('GUI', self.combobox.get())
        acc_name = self.combobox.get()
        password_data = DB.fetch_account_pass(acc_name)
        password = crypto_sys.decrypt_string(password_data)

        return password

    def get_sda(self):
        sda_data = DB.fetch_account_sda(self.combobox.get())
        sda_data = False if sda_data[0] == 'False' else True
        print('GUI', sda_data)

        return sda_data

    def reload_combobox(self, name=None):
        if name:
            self.combobox.insert(-1, name)
            self.combobox.current(0)
            self.draw_widgets()
        else:
            [self.combobox.delete(i) for i in self.combobox.winfo_children()]
            self.combobox = ttk.Combobox(self.root, values=self.fetch_account_names(), state='readonly')
            self.draw_widgets()

    def close_system(self):
        self.root.destroy()

    def run(self):
        self.draw_widgets()
        self.draw_menu()
        self.root.mainloop()


class NewAccountWindow:

    def __init__(self, master):
        self.master = master
        self.root = tk.Toplevel()
        self.root.geometry('230x120+600+300')
        self.root.resizable(False, False)
        self.SDA_var = BooleanVar()
        self.SDA_var.set(0)

        self.name_entry = ttk.Entry(self.root, width=20)
        self.password_entry = ttk.Entry(self.root, width=20, show="*")
        self.btn = ttk.Button(self.root, text="Add Account",
                              command=lambda: self.master.get_data_from_child(self.master.new_window))
        self.name_label = ttk.Label(self.root, text="Login")
        self.password_label = ttk.Label(self.root, text="Password")
        self.j_label = ttk.Label(self.root, text="Enter Data:", font=('Bahnschrift', 10, 'bold'))
        self.message_box = messagebox.showinfo("Info", "Your data is encrypted!!")
        self.sda_checkbox = ttk.Checkbutton(self.root, text="SDA", variable=self.SDA_var, onvalue=1, offvalue=0)
        self.root.grab_set()
        self.root.focus()

        self.draw_widgets()

    def draw_widgets(self):
        self.j_label.grid(column=1, row=0)
        self.name_label.grid(column=0, row=1, padx=2, pady=2)
        self.password_label.grid(column=0, row=2, padx=2, pady=2)
        self.name_entry.grid(column=1, row=1, padx=2, pady=2)
        self.password_entry.grid(column=1, row=2, padx=5, pady=2)
        self.btn.grid(column=1, row=3, sticky='NSEW', padx=3, pady=3)
        self.sda_checkbox.grid(column=0, row=3, padx=3, pady=3)


class ConfigureAccountsWindow:
    counter = False
    # class_examples = 0
    #
    # def __new__(cls, *dt, **mp):  # класса Singleton.
    #     if cls.class_examples == 0:  # Если он еще не создан, то
    #         cls.obj = object.__new__(cls)  # вызовем __new__ родительского класса
    #         cls.class_examples += 1
    #         return cls.obj
    #     else:
    #         return

    def __init__(self, master, account):
        self.master = master
        self.account_name = account

        if ConfigureAccountsWindow.counter:
            return
        else:
            ConfigureAccountsWindow.counter = True

        self.root = tk.Toplevel()
        self.root.bind('<Escape>', lambda e: self.root.destroy())
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.root.geometry('250x120+600+300')
        self.root.resizable(False, False)
        self.root.title("Change Window")
        self.str_var = StringVar(self.root, self.account_name)

        self.account_label = ttk.Label(self.root, text="Login")
        self.password_label = ttk.Label(self.root, text="Password")
        self.account_entry = ttk.Entry(self.root, state='disable', textvariable=self.str_var)
        self.password_entry = ttk.Entry(self.root, show='*')
        self.delete_button = ttk.Button(self.root, text="Delete Account", command=self.delete_account)
        self.accept_changes = ttk.Button(self.root, text="Accept Changes", command=self.accept_changes)

        self.draw_widgets()

    def draw_widgets(self):
        self.account_label.grid(column=0, row=0, padx=5, pady=5, ipadx=2, ipady=2)
        self.password_label.grid(column=0, row=1, padx=5, pady=5, ipadx=2, ipady=2)
        self.account_entry.grid(column=1, row=0, padx=5, pady=5, ipadx=2, ipady=2)
        self.password_entry.grid(column=1, row=1, padx=5, pady=5, ipadx=2, ipady=2)
        self.delete_button.grid(column=0, row=2, padx=5, pady=5, ipadx=2, ipady=2)
        self.accept_changes.grid(column=1, row=2, padx=5, pady=5, ipadx=2, ipady=2)

    def delete_account(self):
        DB.delete_account(self.account_name)
        self.master.combobox = ttk.Combobox(self.root, values=self.master.fetch_account_names(), state='readonly')
        self.master.reload_combobox()
        messagebox.showinfo("Successfull!", "Account successfully deleted!")

    def accept_changes(self):
        passw = self.password_entry.get()
        if len(passw) >= 3:
            DB.update_account(self.account_name, passw)
            messagebox.showinfo("Successfull!", "Changes successfully accepted!")
        else:
            messagebox.showerror("Error!", "Check your data!")
            self.root.grab_set()
            self.root.focus()

    def on_closing(self):
        ConfigureAccountsWindow.counter = False
        self.root.destroy()


app = tk.Tk()
main_window = SteamConnectionGui(app)
main_window.run()
