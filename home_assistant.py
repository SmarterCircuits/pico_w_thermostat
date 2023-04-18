import json
import urequests as requests

class HomeAssistantSettings:
    def __init__(self, from_file:str = None):
        self.enabled = False
        self.api_key = ""
        self.base_url = ""
        self.base_api = f"{self.base_url}/api/"
        self.high_temp_input = "input_number.cool_above"
        self.low_temp_input = "input_number.heat_below"
        self.hvac_enabled_input = "input_boolean.hvac_enabled"
        self.ventilation_enabled_input = "input_boolean.ac_ventilation_assist"
        self.preventilation_time_input = "input_number.ventilation_assist_cycle_time"
        self.circulation_time_input = "input_number.still_air_circulation_time"
        self.circulate_after_input = "input_number.still_air_time_limit"
        self.over_temp_input = "input_number.temperature_target_overshoot"
        self.stage_limit_input = "input_number.stage_limit"
        self.stage_cooldown_input = "input_number.stage_cooldown"
        self.fan_on_output = "binary_sensor.hallway_fan_on"
        self.heat_on_output = "binary_sensor.hallway_heat_on"
        self.ac_on_output = "binary_sensor.hallway_ac_on"
        self.ventilation_on_output = "binary_sensor.hallway_whf_on"
        self.temperature_output = "sensor.hallway_thermostat_temperature"
        self.temperature_offset_input = "input_number.temperature_offset"
        self.unique_id = "picostat"
        self.ventilation_entity_id = ""
        self.use_home_assistant_ventilation = False
        self.console_output = "input_text.hallway_thermostat_console"
        if from_file is not None:
            self.load_from_file(from_file)
        
    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, 
            sort_keys=True, indent=4)
    
    def load_from_file(self, file:str):
        with open(file) as fd:
            data = json.load(fd)
            self.enabled = data["enabled"]
            self.api_key = data["api_key"]
            self.base_url = data["base_url"]
            self.base_api = f"{self.base_url}/api/"
            self.high_temp_input = data["high_temp_input"]
            self.low_temp_input = data["low_temp_input"]
            self.hvac_enabled_input = data["hvac_enabled_input"]
            self.ventilation_enabled_input = data["ventilation_enabled_input"]
            self.preventilation_time_input = data["preventilation_time_input"]
            self.circulation_time_input = data["circulation_time_input"]
            self.over_temp_input = data["over_temp_input"]
            self.stage_limit_input = data["stage_limit_input"]
            self.stage_cooldown_input = data["stage_cooldown_input"]
            self.fan_on_output = data["fan_on_output"]
            self.heat_on_output = data["heat_on_output"]
            self.ac_on_output = data["ac_on_output"]
            self.ventilation_on_output = data["ventilation_on_output"]
            self.temperature_output = data["temperature_output"]
            self.temperature_offset_input = data["temperature_offset_input"]
            self.unique_id = data["unique_id"]
            self.ventilation_entity_id = data["ventilation_entity_id"]
            self.use_home_assistant_ventilation = data["use_home_assistant_ventilation"]
            self.console_output = data["console_output"]

class HomeAssistantHelper:
    def __init__(self, settings: HomeAssistantSettings):
        self.settings = settings
        
    def get_home_assistant_setting(self, setting:str):
        try:
            val = requests.get(f"{self.settings.base_api}states/{setting}",headers={
                "Authorization": f"Bearer {self.settings.api_key}",
                "content-type": "application/json",
            }).json()["state"]
            #print(f"{setting} {val}")
            return val
        except Exception as e:
            print(f"failed to get setting: {self.settings.base_api}states/{setting}")
            print(e)
            return None
        
    def set_ventilation(self, state:str):
        if self.settings.use_home_assistant_ventilation is not True:
            return
        response = None
        try:
            state = {"state":state}
            response = requests.post(f"{self.settings.base_api}states/{self.settings.ventilation_entity_id}",data=json.dumps(state),headers={
                    "Authorization": f"Bearer {self.settings.api_key}",
                    "content-type": "application/json",
                })
        except Exception as e:
            print(f"failed to set ventilation: {state}")
            print(e)
            if response is not None:
                print(response.json())
            # I know I should do better. I'll add logging later maybe, I don't like writing if I don't have to.
            pass
        
    def send_to_home_assistant(self, helper:str, value, uom:str = None):
        if self.settings.enabled is not True:
            return
        response = None
        try:
            state = {"state":value, "unique_id":self.settings.unique_id, "entity_id":helper}
            if uom is not None:
                state = {"state":value, "unique_id":self.settings.unique_id, "entity_id":helper, "attributes": {"unit_of_measurement": uom}}
            response = requests.post(f"{self.settings.base_api}states/{helper}",data=json.dumps(state),headers={
                    "Authorization": f"Bearer {self.settings.api_key}",
                    "content-type": "application/json",
                })
        except Exception as e:
            print(f"failed to set helper: {self.settings.base_api}states/{helper} value:{value}")
            print(e)
            if response is not None:
                print(response.json())
            # I know I should do better. I'll add logging later maybe, I don't like writing if I don't have to.
            pass


