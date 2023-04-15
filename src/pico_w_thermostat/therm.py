import time

from dht11 import DHT11
from machine import ADC, Pin

from .settings import ThermostatSettings
from .state import ThermostatState
from .home_assistant import HomeAssistantHelper, HomeAssistantSettings


class Thermostat:
    def __init__(self):
        self.ha_settings = HomeAssistantSettings()
        self.ha_helper = HomeAssistantHelper(self.ha_settings)
        self.settings = ThermostatSettings()
        self.state = ThermostatState()

        self.heat = Pin(self.settings.heat_pin, Pin.OUT)
        self.fan = Pin(self.settings.fan_pin, Pin.OUT)
        self.ac = Pin(self.settings.ac_pin, Pin.OUT)
        self.heat.on()
        self.fan.on()
        self.ac.on()
        self.sensor = ADC(4)
        self.external_sensor = None

        if self.settings.external_sensor_type == "dht11":
            self.external_sensor = DHT11(
                Pin(self.settings.external_sensor_pin, Pin.OUT, Pin.PULL_DOWN)
            )

        now_time = (time.localtime()[3], time.localtime()[4])

        self.stage_cooldown = False
        self.cooldown_until = now_time
        self.ventilating = False
        self.ventilate_until = now_time
        self.circulate_until = now_time
        self.last_circulation = now_time

    def minutes_from(self, base_time: tuple, sample_time: tuple):
        b = base_time[0] * 60 + base_time[1]
        s = sample_time[0] * 60 + sample_time[1]
        return s - b

    def add_minutes(self, time: tuple, minutes: int):
        h = time[0]
        m = time[1]
        m = m + minutes
        if m > 59:
            h = h + 1
        if h > 23:
            h = 0
        return (h, m)

    def get_temp(self):
        # TODO: fix for C as well
        conversion_factor = 3.3 / (65535)
        reading = self.sensor.read_u16() * conversion_factor
        temperature_c = 27 - (reading - 0.706) / 0.001721
        temperature_f = (temperature_c * 9 / 5) + 32
        return (temperature_c, temperature_f + self.settings.temp_offset)

    def run(self):
        # in case the settings weren't picked up on first run
        if (
            self.settings.external_sensor_type == "dht11"
            and self.external_sensor is None
        ):
            self.external_sensor = DHT11(
                Pin(self.settings.external_sensor_pin, Pin.OUT, Pin.PULL_DOWN)
            )

        now_time = (time.localtime()[3], time.localtime()[4])
        print(f"thermostat run at {now_time}")
        # read temperature
        # TODO: set F or C
        temp = self.get_temp()[1]
        print(f"thermostat on board temp {temp}")
        if self.external_sensor is not None:
            try:
                external_temp_c = self.external_sensor.temperature
                external_temp_f = (external_temp_c * 9 / 5) + 32
                print(f"thermostat external temp {external_temp_f}")
                if self.settings.use_temp_sensor_average:
                    temp = round((temp + external_temp_f) / 2, 2)
                else:
                    temp = external_temp_f
            except:
                print("external sensor read failure")
        print(f"thermostat using temp {temp}")
        self.state.temperature = temp

        # check for settings updates if Home Assistant is present
        self.settings.update_from_home_assistant(self.ha_helper)

        # if the system is in stage cool down, check if it's done
        if self.stage_cooldown and self.cooldown_until == now_time:
            print("cooldown done")
            self.stage_cooldown = False

        # if the system is disabled, make sure nothing is on and stop here.
        if self.settings.hvac_enabled is not True:
            print("system is disabled")
            if self.state.ac_on:
                self.ac.on()
            if self.state.fan_on:
                self.fan.on()
            if self.state.heat_on:
                self.heat.on()
            self.state.report_to_home_assistant(self.ha_helper)
            return

        # if the system is in stage cool down or the override is set, stop here
        if self.stage_cooldown or self.settings.manual_override:
            print("still cooling down or override is set")
            self.state.report_to_home_assistant(self.ha_helper)
            return

        # if the system is cooling and we're not lower than the overshoot temperature, we're in the cooling cycle.
        if (
            self.state.ac_on
            and temp
            > self.settings.temperature_high_setting - self.settings.swing_temp_offset
        ):
            print("system is cooling")
            self.state.report_to_home_assistant(self.ha_helper)
            return

        # if we're ventilating and we're done, start cooling
        if self.ventilating and self.ventilate_until == now_time:
            print("done venting, start cooling")
            self.stop_ventilating()
            self.start_cooling()
            self.state.report_to_home_assistant(self.ha_helper)
            return

        # if we're over temp, we should be in the cooling cycle (I know it's nasty looking, but stop and think about it)
        if temp > self.settings.temperature_high_setting:
            print("over temp")
            if self.settings.use_whole_house_fan:
                print("using whole house fan")
                if self.ventilating:
                    print("still venting, move on")
                    self.state.report_to_home_assistant(self.ha_helper)
                    return
                print("start venting")
                self.state.report_to_home_assistant(self.ha_helper)
                self.start_ventilating(now_time)
                return
            print("not using whole house fan, start cooling")
            self.last_circulation = now_time
            self.start_cooling()
            self.state.report_to_home_assistant(self.ha_helper)
            return

        # if we're not over temp, but the cooling is on, turn it off and stage cool down.
        if self.state.ac_on:
            print("done cooling")
            self.stop_cooling(now_time)
            self.state.report_to_home_assistant(self.ha_helper)
            return

        # if the system is heating and we're not higher than the overshoot temperature, we're in the heating cycle.
        if (
            self.state.heat_on
            and temp
            < self.settings.temperature_low_setting + self.settings.swing_temp_offset
        ):
            print("still heating")
            self.state.report_to_home_assistant(self.ha_helper)
            return

        # if we're under temp, we should be in the heating cycle
        if temp < self.settings.temperature_low_setting:
            print("under temp, start heating")
            self.start_heating()
            self.state.report_to_home_assistant(self.ha_helper)
            return

        # if we're not over temp, but the heating is on, turn it off and stage cool down.
        if self.state.heat_on:
            print("done heating")
            self.stop_heating(now_time)
            self.state.report_to_home_assistant(self.ha_helper)
            return

        # if we're circulating and we're done, stop and stage cool down
        if self.state.fan_on and self.circulate_until == now_time:
            print("done circulating")
            self.stop_circulating(now_time)
            self.state.report_to_home_assistant(self.ha_helper)
            return

        since_last_circulation = self.minutes_from(now_time, self.last_circulation)
        if since_last_circulation >= self.settings.air_circulation_minutes:
            print("start circulating")
            self.start_circulating(now_time)
        self.state.report_to_home_assistant(self.ha_helper)

    def start_circulating(self, now_time: tuple):
        print(f"start_circulating {now_time}")
        self.fan.off()
        self.state.fan_on = True
        self.circulate_until = self.add_minutes(
            now_time, self.settings.circulation_cycle_minutes
        )

    def stop_circulating(self, now_time: tuple):
        print(f"stop_circulating {now_time}")
        self.fan.on()
        self.state.fan_on = False
        self.cool_down_stage(now_time)

    def start_ventilating(self, now_time: tuple):
        print(f"start_ventilating {now_time}")
        self.ha_helper.set_ventilation("on")
        self.ventilate_until = self.add_minutes(
            now_time, self.settings.ventilation_cycle_minutes
        )
        self.ventilating = True

    def stop_ventilating(self):
        print("stop_ventilating")
        self.ha_helper.set_ventilation("off")
        self.ventilating = False

    def start_cooling(self):
        print("start_cooling")
        self.ac.off()
        self.state.ac_on = True

    def stop_cooling(self, now_time: tuple):
        print(f"stop_cooling {now_time}")
        self.ac.on()
        self.state.ac_on = False
        self.cool_down_stage(now_time)

    def start_heating(self):
        print("start_heating")
        self.heat.off()
        self.state.heat_on = True

    def stop_heating(self, now_time: tuple):
        print(f"stop_heating {now_time}")
        self.heat.on()
        self.state.heat_on = False
        self.cool_down_stage(now_time)

    def cool_down_stage(self, now_time: tuple):
        print(f"cool_down_stage {now_time}")
        self.last_circulation = now_time
        self.cooldown_until = self.add_minutes(
            now_time, self.settings.stage_cooldown_minutes
        )
        self.stage_cooldown = True
