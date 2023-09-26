# Makefile for MicroPython on ESP32.
#
# This is a simple, convenience wrapper around idf.py (which uses cmake).

# Select the board to build for, defaulting to GENERIC.
BOARD ?= MixGo_ESP32_LITE

# If the build directory is not given, make it reflect the board name.
BUILD ?= build-$(BOARD)

# Device serial settings.
PORT ?= /dev/ttyUSB0
BAUD ?= 460800

PYTHON ?= python3

#获取micropython版本号
MPY_VERSION = $(shell git -C ../.. describe --tags --abbrev=0)


GIT_SUBMODULES = lib/berkeley-db-1.xx

.PHONY: all clean deploy erase submodules FORCE

CMAKE_ARGS =

ifdef USER_C_MODULES
	CMAKE_ARGS += -DUSER_C_MODULES=${USER_C_MODULES}
endif

IDFPY_FLAGS += -D MICROPY_BOARD=$(BOARD) -B $(BUILD) $(CMAKE_ARGS)

ifdef FROZEN_MANIFEST
       IDFPY_FLAGS += -D MICROPY_FROZEN_MANIFEST=$(FROZEN_MANIFEST)
endif

all:
	idf.py $(IDFPY_FLAGS) build
	@$(PYTHON) makeimg.py \
		$(BUILD)/sdkconfig \
		$(BUILD)/bootloader/bootloader.bin \
		$(BUILD)/partition_table/partition-table.bin \
		$(BUILD)/micropython.bin \
		$(BUILD)/firmware.bin \
		$(BUILD)/micropython.uf2
	@cp $(BUILD)/firmware.bin firmware/$(BOARD)-$(MPY_VERSION).bin

$(BUILD)/bootloader/bootloader.bin $(BUILD)/partition_table/partition-table.bin $(BUILD)/micropython.bin: FORCE

clean:
	idf.py $(IDFPY_FLAGS) fullclean

deploy:
	idf.py $(IDFPY_FLAGS) -p $(PORT) -b $(BAUD) flash

erase:
	idf.py $(IDFPY_FLAGS) -p $(PORT) -b $(BAUD) erase_flash

submodules:
	git submodule update --init $(addprefix ../../,$(GIT_SUBMODULES))

#提取板卡目录文件名
DIRS := $(shell find boards -maxdepth 1 -type d -exec basename {} \;)
DIRS := $(filter-out boards, $(DIRS))

#清除编译
all_clean: 
	@for dir in $(DIRS); do \
		echo "-----------------------------------------------------------------------------------------------------------------------------"; \
		echo "                                            Fullclean $$dir  firmware"; \
		echo "-----------------------------------------------------------------------------------------------------------------------------"; \
		idf.py -D MICROPY_BOARD=$$dir -B build-$$dir  fullclean;\
		rm -rf firmware/$$dir-$(MPY_VERSION).bin;\
	done

#编译固件
all_build: 
	@for dir in $(DIRS); do \
		echo "-----------------------------------------------------------------------------------------------------------------------------"; \
		echo "                                            Compile $$dir  firmware"; \
		echo "-----------------------------------------------------------------------------------------------------------------------------"; \
		idf.py -D MICROPY_BOARD=$$dir -B build-$$dir  build;\
		$(PYTHON) makeimg.py \
			build-$$dir/sdkconfig \
			build-$$dir/bootloader/bootloader.bin \
			build-$$dir/partition_table/partition-table.bin \
			build-$$dir/micropython.bin \
			build-$$dir/firmware.bin \
			build-$$dir/micropython.uf2 ;\
		cp -r build-$$dir/firmware.bin firmware/$$dir-$(MPY_VERSION).bin ;\
	done
