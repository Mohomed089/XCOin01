import uiautomator2 as u2
import time
import threading
from adb_shell.adb_device import AdbDeviceTcp
from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from jnius import autoclass, cast

# Connect to the device
d = u2.connect()

# Set up ADB connection
adb_device = AdbDeviceTcp('127.0.0.1', 5555)
adb_device.connect()

# Check for the "Выполнить" button
if not d(text="Выполнить").exists:
    print("The 'Выполнить' button is not found on the screen, stopping the program.")
else:
    print("Found the 'Выполнить' button.")

# Initialize PythonActivity for Android
PythonActivity = autoclass('org.kivy.android.PythonActivity')
Context = autoclass('android.content.Context')
WindowManager = autoclass('android.view.WindowManager')
LayoutParams = autoclass('android.view.WindowManager$LayoutParams')

class CircularButton(Button):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_normal = ''
        self.size_hint = (None, None)
        self.size = (100, 100)
        self.background_color = (0.3, 0.6, 0.9, 1)
        self.font_size = 20
        self.color = (1, 1, 1, 1)

class MyApp(App):
    def build(self):
        self.root = FloatLayout()

        bottom_layout = BoxLayout(size_hint=(1, None), height=120, spacing=20, padding=20)
        bottom_layout.pos_hint = {'x': 0, 'y': 0}

        self.btn1 = CircularButton(text="Start")
        self.btn2 = CircularButton(text="Stop")

        self.btn1.bind(on_press=self.start_loop)
        self.btn2.bind(on_press=self.stop_loop)

        bottom_layout.add_widget(self.btn1)
        bottom_layout.add_widget(self.btn2)

        self.root.add_widget(bottom_layout)

        self.create_floating_window()

        return self.root

    def create_floating_window(self):
        activity = PythonActivity.mActivity
        context = cast('android.content.Context', activity.getApplicationContext())
        self.wm = cast('android.view.WindowManager', context.getSystemService(Context.WINDOW_SERVICE))

        self.params = LayoutParams()
        self.params.width = LayoutParams.WRAP_CONTENT
        self.params.height = LayoutParams.WRAP_CONTENT
        self.params.type = LayoutParams.TYPE_APPLICATION_OVERLAY
        self.params.flags = LayoutParams.FLAG_NOT_FOCUSABLE
        self.params.x = 100
        self.params.y = 100

        self.floating_button = Button(text="Floating Button", size_hint=(None, None), size=(100, 100))
        self.wm.addView(self.floating_button, self.params)

    def remove_floating_window(self):
        if self.floating_button:
            self.wm.removeView(self.floating_button)

    def on_pause(self):
        self.remove_floating_window()
        return True

    def on_resume(self):
        self.create_floating_window()

    def start_loop(self, instance):
        self.running = True
        self.loop_thread = threading.Thread(target=self.run_loop)
        self.loop_thread.start()

    def stop_loop(self, instance):
        self.running = False
        if hasattr(self, 'loop_thread') and self.loop_thread.is_alive():
            self.loop_thread.join()

    def run_loop(self):
        if not d(text="Выполнить").exists:
            print("The 'Выполнить' button is not found, stopping the program.")
            return
        else:
            print("Found the 'Выполнить' button.")

        while self.running:
            print("Searching for the 'Выполнить' button...")
            time.sleep(3)

            if d(text="Выполнить").exists:
                d(text="Выполнить").click()
                print("Clicked the 'Выполнить' button")
                
                time.sleep(3)
                
                if d(text="following").exists:
                    d(text="following").click()
                    print("Clicked the 'following' button")
                else:
                    print("The 'following' button is not found.")
                
                time.sleep(3)
                adb_device.shell("am start -n com.android.chrome/com.google.android.apps.chrome.Main")
                print("Returned to Chrome browser.")
            else:
                print("The 'Выполнить' button is not found, stopping the process.")
                break

if __name__ == '__main__':
    MyApp().run()
