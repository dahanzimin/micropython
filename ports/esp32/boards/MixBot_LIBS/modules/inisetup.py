import uos
from flashbdev import bdev


def check_bootsec():
    buf = bytearray(bdev.ioctl(5, 0))  # 5 is SEC_SIZE
    bdev.readblocks(0, buf)
    empty = True
    for b in buf:
        if b != 0xFF:
            empty = False
            break
    if empty:
        return True
    fs_corrupted()


def fs_corrupted():
    import time

    while 1:
        print(
            """\
The filesystem appears to be corrupted. If you had important data there, you
may want to make a flash snapshot to try to recover it. Otherwise, perform
factory reprogramming of MicroPython firmware (completely erase flash, followed
by firmware programming).
"""
        )
        time.sleep(3)


def setup():
    check_bootsec()
    print("Performing initial setup")
    uos.VfsLfs2.mkfs(bdev)
    vfs = uos.VfsLfs2(bdev)
    uos.mount(vfs, "/")
    with open("boot.py", "w") as f:
        f.write(
            """\
#Press the key to interrupt the startup and shutdown program
from machine import Pin
from time import  sleep

def irq_func(power_key):
    sleep(0.05)
    if power_key.value():
        sleep(0.05)
        if power_key.value():
            power_en.value(not power_en.value())

power_en = Pin(5,  Pin.OUT)
power_key = Pin(34, Pin.IN )
power_key.irq(handler= irq_func, trigger= Pin.IRQ_RISING)
power_en.value(1)

if not Pin(39, Pin.IN, Pin.PULL_UP).value():
    from neopixel import NeoPixel
    _rgb = NeoPixel(Pin(12), 2)
    _rgb.fill((10, 0, 0))
    _rgb.write()
    print("Entering forced blocking mode")
    while True:
        pass

"""
        )
    return vfs
