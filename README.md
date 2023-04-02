# pico_w_thermostat

This code is for a DIY smart thermostat based on a Raspberry Pi Pico W and is intended to integrate with Home Assistant, MQTT, or be used as a stand-alone device.

This code relies on the correct firmware to be installed on the Pico which includes the network module.

This version of the firmware can be found here:

https://peppe8o.com/download/micropython/firmware/micropython-firmware-pico-w-290622.uf2

  

In order to install it, hold the boot button on the Pico W, connect the USB cable, and drop the uf2 file into the drive that becomes available. Once it has copied, the Pico should reconnect as itself and be accessible through your IDE.

  

This project also relies on the micropython-ssd1306 module.

  

## Using with Home Assistant

  

You will need your Long-Life Key to access Home Assistant from the Pico W Thermostat. Just paste it into the appropriate setting in the home_assistant.json file.

In order to control and configure your thermostat with Home Assistant, you'll need to set up a few helpers. You won't need to worry about the helpers for data sent from the thermostat as these will be created automatically.

Below are the recommended helpers and their purpose. You may omit any of these and the default setting or local setting programmed via buttons or MQTT message will be used.

  
|home_assistant.json key|recommended helper/entity type|recommended entity name|purpose|
|--|--|--|--|
|circulate_after_input|input_number|still_air_time_limit|how many minutes to wait since the last time heating, cooling, or circulation ended before circulating air|
|circulation_time_input|input_number|still_air_circulation_time|how many minutes circulating cycle should run when circulate_air_input has been reached|
|high_temp_input|input_number|cool_above|
|hvac_enabled_input|input_boolean|hvac_enabled|
|low_temp_input|input_number|heat_below|
|over_temp_input|input_number|temperature_target_overshoot|
|preventilation_time_input|input_number|ventilation_assist_cycle_time|
|stage_cooldown_input|input_number|stage_cooldown|
|stage_limit_input|input_number|stage_limit|
|ventilation_enabled_input|input_boolean|ac_ventilation_assist|

  
  

## Features to be added:

- MQTT support

- Actually use the whole house fan (needs the on command which will send a message to either MQTT or Home Assistant depending on how your fan is set up).

- DHT22 support