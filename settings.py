import json
from home_assistant import HomeAssistantHelper

class ThermostatSettings:
    def __init__(self, from_file:str = None):
        self.room = "hallway"
        self.wifi_ssid = ""
        self.wifi_pass = ""
        self.run_every_seconds = 10
        self.failed_read_halt_limit = 10
        self.temperature_high_setting = 73
        self.temperature_low_setting = 69
        self.air_circulation_minutes = 30
        self.circulation_cycle_minutes = 10
        self.ventilation_cycle_minutes = 10
        self.stage_limit_minutes = 15
        self.stage_cooldown_minutes = 5
        self.use_whole_house_fan = False
        self.hvac_enabled = True
        self.swing_temp_offset = 1
        self.manual_override = False
        self.ac_pin = 10
        self.fan_pin = 11
        self.heat_pin = 12
        if from_file is not None:
            self.load_from_file(from_file)
        
    def toJSON(self):
        # not sure why I'm getting "extra keywords given" error, going the ugly way for now
        #return json.dumps(self, default=lambda o: o.__dict__, 
        #    sort_keys=True, indent=4)
        return json.dumps({
            "room": self.room,
            "wifi_ssid": self.wifi_ssid,
            "wifi_pass": self.wifi_pass,
            "run_every_seconds": self.run_every_seconds,
            "failed_read_halt_limit": self.failed_read_halt_limit,
            "temperature_high_setting": self.temperature_high_setting,
            "temperature_low_setting": self.temperature_low_setting,
            "air_circulation_minutes": self.air_circulation_minutes,
            "circulation_cycle_minutes": self.circulation_cycle_minutes,
            "ventilation_cycle_minutes": self.ventilation_cycle_minutes,
            "stage_limit_minutes": self.stage_limit_minutes,
            "stage_cooldown_minutes": self.stage_cooldown_minutes,
            "use_whole_house_fan": self.use_whole_house_fan,
            "hvac_enabled": self.hvac_enabled,
            "swing_temp_offset": self.swing_temp_offset,
            "manual_override": self.manual_override,
            "ac_pin": self.ac_pin,
            "fan_pin": self.fan_pin,
            "heat_pin": self.heat_pin
        })
    
    def save_to_file(self, file):
        with open(file) as fd:
            fd.write(self.toJSON())
            fd.close()
    
    def load_from_file(self, file):
        with open(file) as fd:
            data = json.load(fd)
            self.room = data["room"]
            self.heat_pin = data["heat_pin"]
            self.ac_pin = data["ac_pin"]
            self.fan_pin = data["fan_pin"]
            self.run_every_seconds = data["run_every_seconds"]
            self.failed_read_halt_limit = data["failed_read_halt_limit"]
            self.temperature_high_setting = data["temperature_high_setting"]
            self.temperature_low_setting = data["temperature_low_setting"]
            self.air_circulation_minutes = data["air_circulation_minutes"]
            self.circulation_cycle_minutes = data["circulation_cycle_minutes"]
            self.ventilation_cycle_minutes = data["ventilation_cycle_minutes"]
            self.stage_limit_minutes = data["stage_limit_minutes"]
            self.stage_cooldown_minutes = data["stage_cooldown_minutes"]
            self.use_whole_house_fan = data["use_whole_house_fan"]
            self.hvac_enabled = str(data["hvac_enabled"]).lower() == "false"
            self.swing_temp_offset = data["swing_temp_offset"]
        
    def update_from_home_assistant(self, helper: HomeAssistantHelper):
        if helper.settings.enabled is False:
            return
        
        # I would love to do this in one call. Not sure if HA can do this, but I'm looking into it.
        high_temp = helper.get_home_assistant_setting(helper.settings.high_temp_input)
        if high_temp is not None:
            self.temperature_high_setting = float(high_temp)
        
        low_temp = helper.get_home_assistant_setting(helper.settings.low_temp_input)
        if low_temp is not None:
            self.temperature_low_setting = float(low_temp)
        
        circ_time = helper.get_home_assistant_setting(helper.settings.circulation_time_input)
        if circ_time is not None:
            self.circulation_cycle_minutes = int(circ_time)
        
        still_time = helper.get_home_assistant_setting(helper.settings.circulate_after_input)
        if still_time is not None:
            self.air_circulation_minutes = int(still_time)
        
        stage_limit = helper.get_home_assistant_setting(helper.settings.stage_limit_input)
        if stage_limit is not None:
            self.stage_limit_minutes = int(stage_limit)
        
        stage_cooldown = helper.get_home_assistant_setting(helper.settings.stage_cooldown_input)
        if stage_cooldown is not None:
            self.stage_cooldown_minutes = int(stage_cooldown)
        
        over_temp = helper.get_home_assistant_setting(helper.settings.over_temp_input)
        if over_temp is not None:
            self.swing_temp_offset = int(over_temp)
        
        use_vent = helper.get_home_assistant_setting(helper.settings.ventilation_enabled_input)
        if use_vent is not None:
            self.use_whole_house_fan = use_vent.lower() == "on"
        
        hvac_enabled = helper.get_home_assistant_setting(helper.settings.hvac_enabled_input)
        if hvac_enabled is not None:
            self.hvac_enabled = hvac_enabled.lower() == "on"
        
        self.save_to_file('settings.json')

