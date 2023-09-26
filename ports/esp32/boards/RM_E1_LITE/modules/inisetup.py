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

def irq_func(ikey):
    sleep(0.05)
    if ikey.value():
        sleep(0.05)
        if ikey.value():
            flag=ccen.value()
            gled.value( not flag)
            ccen.value( not flag)

gled = Pin(4,  Pin.OUT)
ccen = Pin(5,  Pin.OUT)
ikey = Pin(34, Pin.IN )
ikey.irq(handler= irq_func, trigger= Pin.IRQ_RISING)
gled.value(1)
ccen.value(1)

"""
        )
    return vfs
