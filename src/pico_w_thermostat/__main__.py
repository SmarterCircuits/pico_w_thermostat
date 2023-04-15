import time
import network

from .therm import Thermostat
from .button import Button
from .display import Display


def main():

    thermostat = Thermostat()
    thermostat.ha_settings.load_from_file("home_assistant.json")
    thermostat.settings.load_from_file("settings.json")
    screen = Display(8, 9)
    setting_select = "low temp"

    def show_screen(pre=""):
        state = "idle"
        if thermostat.ventilating:
            state = "ventilating"
        if thermostat.state.ac_on:
            state = "cooling"
        if thermostat.state.fan_on:
            state = "circulating"
        if thermostat.state.heat_on:
            state = "heating"
        if thermostat.settings.hvac_enabled is not True:
            state = "DISABLED"
        screen.display_text(
            f"{pre}{thermostat.state.temperature} F ---------------- : {state} : ----------------  {thermostat.settings.temperature_low_setting} ----- {thermostat.settings.temperature_high_setting} ---------------- set {setting_select}"
        )

    def btn_up_press():
        if setting_select == "high temp":
            thermostat.settings.temperature_high_setting = (
                thermostat.settings.temperature_high_setting + 1
            )
        elif setting_select == "low temp":
            thermostat.settings.temperature_low_setting = (
                thermostat.settings.temperature_low_setting + 1
            )
        elif setting_select == "system":
            thermostat.settings.hvac_enabled = thermostat.settings.hvac_enabled is False
        show_screen()

    def btn_down_press():
        if setting_select == "high temp":
            thermostat.settings.temperature_high_setting = (
                thermostat.settings.temperature_high_setting - 1
            )
        elif setting_select == "low temp":
            thermostat.settings.temperature_low_setting = (
                thermostat.settings.temperature_low_setting - 1
            )
        elif setting_select == "system":
            thermostat.settings.hvac_enabled = thermostat.settings.hvac_enabled is False
        show_screen()

    def btn_m_press():
        nonlocal setting_select
        if setting_select == "high temp":
            setting_select = "low temp"
        elif setting_select == "low temp":
            setting_select = "system"
        elif setting_select == "system":
            setting_select = "high temp"
        show_screen()

    # Connect to the Wi-Fi network
    sta_if = network.WLAN(network.STA_IF)
    sta_if.active(True)
    sta_if.connect(thermostat.settings.wifi_ssid, thermostat.settings.wifi_pass)

    # Wait for the connection to be established
    screen.display_text("connecting wifi...")

    # TODO: add a timeout? what if we never connect?
    while not sta_if.isconnected():
        thermostat.run()
        show_screen("!^ ")
        time.sleep(2)

    btn_up = Button(2, on_up=btn_up_press)
    btn_m = Button(3, on_up=btn_m_press)
    btn_down = Button(4, on_up=btn_down_press)

    ticks = 0
    while True:
        btn_up.update()
        btn_m.update()
        btn_down.update()
        if ticks == 0:
            thermostat.run()
            show_screen()
            ticks = thermostat.settings.run_every_seconds * 10
        ticks = ticks - 1
        time.sleep(0.1)


if __name__ == "__main__":
    raise SystemExit(main)
