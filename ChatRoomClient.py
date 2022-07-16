from kivy.app import App
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.lang import Builder
from kivy.properties import ObjectProperty
from kivy.properties import StringProperty
from kivy.uix.popup import Popup
from kivy.uix.floatlayout import FloatLayout
import threading
import sys
import socket
import errno
from kivy.clock import Clock
from BazyDanych.UsersDataBase import write_to_db, rows
from kivy.core.window import Window

HEADER_LENGTH = 10
IP = "127.0.0.1"
PORT = 1234

if_connected = ""

try:
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((IP, PORT))
    client_socket.setblocking(False)
    if_connected = "Online"
except Exception as e:
    print(f"Connection error {e}")
    if_connected = "Offline"


class RegisterWindow(Screen):
    username_reg = ObjectProperty(None)
    email_reg = ObjectProperty(None)
    password_reg = ObjectProperty(None)
    submit = ObjectProperty(None)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        #print(if_connected)
        if if_connected == "Offline":
            Clock.schedule_once(connection_error)
        Clock.schedule_once(self.set_name_focus)

    def set_name_focus(self, _):
        self.username_reg.focus = True

    def on_enter_text_input(self):
        self.email_reg.focus = True

    def on_enter_text_input2(self):
        self.password_reg.focus = True

    def save_user(self):
        username_db = self.username_reg.text
        email_db = self.email_reg.text
        password_db = self.password_reg.text
        checker = ""

        if not rows:
            if len(username_db) > 0 and len(email_db) > 0 and len(password_db) > 0 and username_db:

                write_to_db(username_db, email_db, password_db)
                sm.current = "login"
            else:
                register_error1()

        else:
            if len(username_db) > 0 and len(email_db) > 0 and len(password_db) > 0 and username_db:
                if len(password_db) >= 8:
                    if email_db.count("@") == 1 and email_db.count(".") > 0:
                        for row in rows:
                            if username_db == row[0] or email_db == row[1]:
                                checker = 0
                                break
                            else:
                                checker = 1
                        if checker == 1:
                            write_to_db(username_db, email_db, password_db)
                            sm.current = "login"
                        else:
                            register_error4()
                    else:
                        register_error5()
                else:
                    register_error3()
            else:
                register_error1()

        self.username_reg.text = ""
        self.email_reg.text = ""
        self.password_reg.text = ""

class ChatWindow(Screen):
    msg_chat = ObjectProperty("")
    dummy_v = StringProperty("")
    login = ObjectProperty()
    join_btn = ObjectProperty(None)
    chat_input = ObjectProperty(None)
    send_button = ObjectProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Window.bind(on_key_down=self._on_keyboard_down)

    def _on_keyboard_down(self, instance, keyboard, keycode, text, modifiers):
        if keycode == 40:  # 40 - Enter key pressed
            if self.send_button.disabled is True:
                pass
            else:
                self.start_sending()
                self.text_msg.focus = False

    def logout(self):
        v = App.get_running_app()
        v.stop_listening = 1
        self.chat_input.text = ""
        sm.current = "login"
        v.stop_listening = 0

    def join2(self):

        self.text_msg.disabled = False
        self.join_btn.disabled = True
        Clock.schedule_once(self.start_listening)
        self.text_msg.focus = True

    def listen(self):
        global my_username
        global msg

        try:
            my_username = App.get_running_app().user_login
            username = my_username.encode('utf-8')
            username_header = f"{len(username):<{HEADER_LENGTH}}".encode('utf-8')
            client_socket.send(username_header + username)
            print("Listening...")

            while True:

                stop = App.get_running_app().stop_listening
                if stop == 1:
                    my_username = ""
                    break
                try:
                    username_header = client_socket.recv(HEADER_LENGTH)
                    username_length = int(username_header.decode('utf-8').strip())
                    username = client_socket.recv(username_length).decode('utf-8')

                    message_header = client_socket.recv(HEADER_LENGTH)
                    message_length = int(message_header.decode('utf-8').strip())
                    message = client_socket.recv(message_length).decode('utf-8')
                    print("kekww: ", message)

                    print(f"{username}: {message}")
                    msg = f"{username}: {message}"
                    self.msg_chat += msg + "\n"

                except IOError as e:
                    if e.errno != errno.EAGAIN and e.errno != errno.EWOULDBLOCK:  # Bledy ktore mozemy napotkac
                        print("Reading error", e)
                        sys.exit()
                    continue

                except Exception as e:
                    print('General error', e)
                    sys.exit()

        except Exception as e:
            print(f"Listening error: {e}")
            Clock.schedule_once(connection_error)
            self.join_btn.disabled = False

    def start_listening(self, _):
        threading.Thread(target=self.listen).start()

    def send_msg(self):

        message = msg_
        try:
            if message:
                message = message.encode('utf-8')
                message_header = f"{len(message):<{HEADER_LENGTH}}".encode('utf-8')
                client_socket.send(message_header + message)
                print(f"{my_username}: {message}")
                self.msg_chat += f"{my_username}: {message.decode()}" + "\n"
        except Exception as e:
            print(f"Sending message error: {e}")
            self.join_btn.disabled = False
            Clock.schedule_once(connection_error)

    def start_sending(self):
        global msg_
        self.text_msg.focus = True
        msg_ = self.text_msg.text
        print(msg_)
        self.send_msg()
        self.text_msg.text = ""


class LoginWindow(Screen):
    login_log = ObjectProperty(None)
    password_log = ObjectProperty(None)
    login_btn = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(LoginWindow, self).__init__(**kwargs)
        #Clock.schedule_once(self.set_name_focus)
#        Window.bind(on_key_down=self._on_keyboard_down)

    def login(self):
        var = App.get_running_app()
        var.user_login = self.login_log.text
        username = self.login_log.text
        password = self.password_log.text
        checker = ""
        if len(username) > 0 and len(password) > 0:
            for row in rows:
                if username == row[0] and password == row[2]:

                    checker = 1
                    sm.current = "chat"
                    break
                else:
                    checker = 0
            if checker == 0:
                login_error2()
        else:
            login_error()

        self.login_log.text = ""
        self.password_log.text = ""


class ScreensManager(ScreenManager):
    login_screen = ObjectProperty(None)
    register_screen = ObjectProperty(None)
    chat_screen = ObjectProperty(None)


class PopUpLogin(FloatLayout):
    @staticmethod
    def close():
        popupWindow_log_err_1.dismiss()


class PopUpLogin2(FloatLayout):
    @staticmethod
    def close():
        popupWindow_log_err_2.dismiss()


class PopUpRegister1(FloatLayout):
    @staticmethod
    def close():
        popupWindow_reg_err_1.dismiss()


class PopUpRegister3(FloatLayout):
    @staticmethod
    def close():
        popupWindow_reg_err_3.dismiss()


class PopUpRegister4(FloatLayout):
    @staticmethod
    def close():
        popupWindow_reg_err_4.dismiss()


class PopUpRegister5(FloatLayout):
    @staticmethod
    def close():
        popupWindow_reg_err_5.dismiss()


class PopUpConnection(FloatLayout):
    @staticmethod
    def close():
        popupWindow_con_err.dismiss()


def login_error():
    global popupWindow_log_err_1
    show = PopUpLogin()

    popupWindow_log_err_1 = Popup(
        title="Error!",
        content=show,
        size_hint=(None, None),
        size=(400, 400),
        background="tlo1.jpg"
    )
    popupWindow_log_err_1.open()


def login_error2():
    global popupWindow_log_err_2
    show = PopUpLogin2()

    popupWindow_log_err_2 = Popup(
        title="Error!",
        content=show,
        size_hint=(None, None),
        size=(400, 400),
        background="tlo1.jpg"
    )
    popupWindow_log_err_2.open()


def register_error1():
    global popupWindow_reg_err_1
    show = PopUpRegister1()

    popupWindow_reg_err_1 = Popup(
        title="Error!",
        content=show,
        size_hint=(None, None),
        size=(400, 400),
        background="tlo1.jpg"
    )
    popupWindow_reg_err_1.open()


def register_error3():
    global popupWindow_reg_err_3
    show = PopUpRegister3()

    popupWindow_reg_err_3 = Popup(
        title="Error!",
        content=show,
        size_hint=(None, None),
        size=(400, 400),
        background="tlo1.jpg"
    )
    popupWindow_reg_err_3.open()


def register_error4():
    global popupWindow_reg_err_4
    show = PopUpRegister4()

    popupWindow_reg_err_4 = Popup(
        title="Error!",
        content=show,
        size_hint=(None, None),
        size=(400, 400),
        background="tlo1.jpg"
    )
    popupWindow_reg_err_4.open()


def register_error5():
    global popupWindow_reg_err_5
    show = PopUpRegister5()

    popupWindow_reg_err_5 = Popup(
        title="Error!",
        content=show,
        size_hint=(None, None),
        size=(400, 400),
        background="tlo1.jpg"
    )
    popupWindow_reg_err_5.open()


def connection_error(_):
    global popupWindow_con_err
    show = PopUpConnection()

    popupWindow_con_err = Popup(
        title="Connection error occurred!",
        content=show,
        size_hint=(None, None),
        size=(400, 400),
        background="tlo1.jpg"
    )
    popupWindow_con_err.open()


kv = Builder.load_file("ChatRoom.kv")


class MyApp(App):
    user_login = ""
    stop_listening = 0
    if_join = 0

    def build(self):
        return sm


sm = ScreenManager()

screens = [RegisterWindow(name='register'), LoginWindow(name="login"), ChatWindow(name="chat")]
for screen in screens:
    sm.add_widget(screen)
sm.current = "register"


if __name__ == "__main__":
    MyApp().run()
