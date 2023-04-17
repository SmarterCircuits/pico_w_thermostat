# pico_w_thermostat

## URGENT BUG NOTICE:
Currently, if the device loses power during a configuration file write, the end of the file will be duplicated and the json parsing will fail, halting the thermostat. The only fix at the moment is to resave the configuration file and restart the thermostat. I have tried wrapping the file load in a try/except, but this results in an EPERM error. I am considering removing the save to file feature that updates the configuration based on incoming Home Assistant (or MQTT) data. I think this would be alright since the default config would be overwritten as soon as the thermostat connected to another system where the setting would still be the same.
I will have an update to the code as soon as possible--hopefully today (4/17/23).

### UPDATE: BUG FIX
The issue descirbed above has been resolved by simply not saving changes as I mentioned. It's not really necessary anyway. Please pull updated code if you have not done so already. 
****

This code is for a DIY smart thermostat based on a Raspberry Pi Pico W and is intended to integrate with Home Assistant, MQTT, or be used as a stand-alone device.

This code relies on the correct firmware to be installed on the Pico which includes the network module.

This version of the firmware can be found here:

https://peppe8o.com/download/micropython/firmware/micropython-firmware-pico-w-290622.uf2

  

In order to install it, hold the boot button on the Pico W, connect the USB cable, and drop the uf2 file into the drive that becomes available. Once it has copied, the Pico should reconnect as itself and be accessible through your IDE.

  

This project also relies on the micropython-ssd1306 module.

  

## Using with Home Assistant

**IMPORTANT: This project is not in any way associated with, endorsed by, or supported by Home Assistant or any of their engineers. This is only meant to work with Home Assistant because it is what I use.**  

You will need your Long-Life Key to access Home Assistant from the Pico W Thermostat. Just paste it into the appropriate setting in the home_assistant.json file.

In order to control and configure your thermostat with Home Assistant, you'll need to set up a few helpers. You won't need to worry about the helpers for data sent from the thermostat as these will be created automatically.

Below are the recommended helpers and their purpose. You may omit any of these and the default setting or local setting programmed via buttons or MQTT message will be used.

  
|home_assistant.json key|recommended helper/entity type|recommended entity name|purpose|
|--|--|--|--|
|circulate_after_input|input_number|still_air_time_limit|how many minutes to wait since the last time heating, cooling, or circulation ended before circulating air|
|circulation_time_input|input_number|still_air_circulation_time|how many minutes circulating cycle should run when circulate_air_input has been reached|
|high_temp_input|input_number|cool_above|temperature at which the cooling cycle is started when the system is enabled|
|low_temp_input|input_number|heat_below|temperature at which the heating cycle is started when the system is enabled|
|hvac_enabled_input|input_boolean|hvac_enabled|if the system is disabled, it will report temperature readings but not run any cycle|
|over_temp_input|input_number|temperature_target_overshoot|how many degrees beyond cycle start temp the system should continue to heat or cool before shutting off|
|preventilation_time_input|input_number|ventilation_assist_cycle_time|how many minutes the ventilation should run prior to the cooling cycle if ventilation is enabled|
|stage_cooldown_input|input_number|stage_cooldown|how many minutes the system must wait before starting another cycle after the previous one stops|
|stage_limit_input|input_number|stage_limit|how many minutes any cycle can run at most|
|ventilation_enabled_input|input_boolean|ac_ventilation_assist|whether or not the system runs a ventilation fan before cooling cycles|

  
  

## Features to be added:

- MQTT support

- Actually use the ventilation cycle (needs the "on" command which will send a message to either MQTT or Home Assistant depending on how your fan is set up).

- External sensor support (doesn't have to be a DHT11 or DHT22, I will be testing several sensors and including instructions for setting up each)