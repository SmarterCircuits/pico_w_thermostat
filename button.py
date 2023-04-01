from machine import Pin

class Button:
    def __init__(self, pin):
        self.pin = Pin(pin, Pin.IN, Pin.PULL_DOWN)
        self.pressed = False
        self.on_down = None
        self.on_up = None

    def update(self):
        pressed = self.pin.value() > 0
        if pressed != self.pressed:
            self.pressed = pressed
            self.handle_button()
            return True
        return False

    def handle_button(self):
        if self.pressed and self.on_down is not None:
            self.on_down()
        if self.pressed is False and self.on_up is not None:
            self.on_up()
