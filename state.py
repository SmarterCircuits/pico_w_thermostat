from home_assistant import HomeAssistantHelper

class ThermostatState:
    def __init__(self):
        self.temperature = None
        self.heat_on = False
        self.ac_on = False
        self.fan_on = False
        self.whf_on = False
    
    def to_list(self):
        return [self.temperature, self.ac_on, self.fan_on, self.heat_on, self.whf_on]
        
    def report_to_home_assistant(self, helper: HomeAssistantHelper):
        if helper.settings.enabled is False:
            return
        
        # Again, I'm looking into how to do this in one call versus multiple.
        heat_on = "off"
        if self.heat_on:
            heat_on = "on"
        helper.send_to_home_assistant(helper.settings.heat_on_output,heat_on)

        fan_on = "off"
        if self.fan_on:
            fan_on = "on"
        helper.send_to_home_assistant(helper.settings.fan_on_output,fan_on)

        ac_on = "off"
        if self.ac_on:
            ac_on = "on"
        helper.send_to_home_assistant(helper.settings.ac_on_output,ac_on)

        whf_on = "off"
        if self.whf_on:
            whf_on = "on"
        helper.send_to_home_assistant(helper.settings.ventilation_on_output,whf_on)

        if self.temperature is not None:
            helper.send_to_home_assistant(helper.settings.temperature_output,self.temperature)
