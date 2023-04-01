from ssd1306 import SSD1306_I2C
from machine import Pin, PWM, I2C
import math

class Display:
    def __init__(self, data_pin, clock_pin):
        i2c = I2C(0, sda=Pin(data_pin), scl=Pin(clock_pin), freq=200000)
        devices = i2c.scan()
        self.detected = True
        self.cycle = 0
        self.asleep = False
        if len(devices) == 0:
            self.detected = False
            return
        self.oled = SSD1306_I2C(128,64,i2c)
    
    def display_text(self, text, centered = False):
        if self.detected is False:
            print(text)
            return
        if self.asleep:
            self.wake()
        self.oled.fill(0)
        stringy = isinstance(text, str)
        if stringy and len(text) > 16:
            stringy = False
            text = self.wrap(text)
        if centered:
            if stringy:
                text = self.center(text)
            else:
                for i in range(len(text)):
                    text[i] = self.center(text[i])
        for i in range(len(text)):
            if stringy:
                y = math.floor(i/16)
                x = i-(y*16)
            else:
                y = i
                x = 0
            self.oled.text(text[i],x*8,y*8)
        self.oled.show()
    
    def center(self, text):
        while len(text) < 16:
            text = ' ' + text + ' '
        return text
    
    def wrap(self, text):
        current_line = ''
        lines = []
        words = text.split()
        for word in words:
            if len(current_line + word) > 16:
                lines.append(current_line)
                current_line = word + ' '
            else:
                current_line = current_line + word + ' '
        if current_line != lines[len(lines)-1]:
            lines.append(current_line)
        return lines
    
    def wake(self):
        self.oled.poweron()
        self.asleep = False
        self.cycle = 0

    def update(self, input):
        if input:
            self.cycle = 0
            return
        
        self.cycle = self.cycle + 1
        
        if self.cycle > 6000:
            if self.asleep:
                self.oled.poweron()
                self.asleep = False
                self.cycle = 5000
            else:
                self.oled.poweroff()
                self.asleep = True
                self.cycle = 0

