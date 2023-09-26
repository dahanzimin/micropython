freeze("modules")
freeze("$(MPY_DIR)/drivers/mixly2.0_src/boards/default/micropython_esp32/build/lib", "mixgo.py")
freeze("$(MPY_DIR)/drivers/mixly2.0_src/boards/default/micropython_common/build/lib")
freeze("$(MPY_DIR)/tools", ("upip.py", "upip_utarfile.py"))
#freeze("$(MPY_DIR)/ports/esp8266/modules", "ntptime.py")
freeze("$(MPY_DIR)/drivers/dht", "dht.py")
freeze("$(MPY_DIR)/drivers/onewire")
include("$(MPY_DIR)/extmod/uasyncio/manifest.py")
include("$(MPY_DIR)/extmod/webrepl/manifest.py")
include("$(MPY_DIR)/drivers/neopixel/manifest.py")
