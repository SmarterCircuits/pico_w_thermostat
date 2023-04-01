# pico_w_thermostat
This code is for a DIY smart thermostat based on a Raspberry Pi Pico W and is intended to integrate with Home Assistant.

this code relies on the correct firmware to be installed on the Pico that includes the network module.

It also relies on the ssd1306 module.

More documentation pending.

Features to be added:
MQTT support
Actually use the whole house fan (needs the on command which will send a message to either MQTT or Home Assistant depending on how your fan is set up).
