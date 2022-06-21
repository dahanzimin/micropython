import time

class Button:
	def __init__(self, pin):
		from machine import Pin
		self._pin = Pin(pin, Pin.IN)
		self._flag = True

	def get_presses(self, delay = 1):
		last_time,presses = time.time(), 0
		while time.time() < last_time + delay:
			time.sleep(0.05)
			if self.was_pressed():
				presses += 1
		return presses

	def is_pressed(self):
		return self._pin.value() == False

	def was_pressed(self):
		if self._pin.value() != self._flag:
			time.sleep(0.01)
			self._flag = self._pin.value()
			if self._flag:
				return False
			else:
				return True

	def irq(self, handler, trigger):
		self._pin.irq(handler = handler, trigger = trigger)

button_a = Button(17)
button_b = Button(16)

class TouchPad:
	def __init__(self, pin,value=220):
		from machine import TouchPad, Pin
		self._pin = TouchPad(Pin(pin))
		self.value = value
		
	def is_touched(self):
		return self._pin.read()	< self.value

touch1 = TouchPad(32)
touch2 = TouchPad(33)
#touch3 = TouchPad(25)
#touch4 = TouchPad(26)

class ADCSensor:
	__species = {}
	__first_init = True
	def __new__(cls, pin, *args, **kwargs):
		if pin not in cls.__species.keys():
			cls.__first_init = True
			cls.__species[pin]=object.__new__(cls)
		return cls.__species[pin]

	def __init__(self, pin):
		if self.__first_init:
			from machine import ADC, Pin
			self.__first_init = False
			self._adc=ADC(Pin(pin))
			self._adc.atten(ADC.ATTN_11DB) 
			self._switch = Pin(15, Pin.OUT)

	def read(self):
		return self._adc.read()
	
	def switch(self,val):
		self._switch.value(val)
		
def infrared_left():
	ADCSensor(34).switch(1)
	time.sleep(0.02)
	adc=ADCSensor(34).read()
	ADCSensor(34).switch(0)	
	return 	adc	

def infrared_right():
	ADCSensor(36).switch(1)
	time.sleep(0.02)
	adc=ADCSensor(36).read()
	ADCSensor(36).switch(0)	
	return 	adc		

def get_brightness():
	return ADCSensor(39).read() 

def get_soundlevel():  
	value_d= []
	for _ in range(5):
		values = []
		for _ in range(5):
			val = ADCSensor(35).read() 
			values.append(val)
		value_d.append(max(values) - min(values))
	return  max(value_d)

try :
	from machine import Pin,SoftI2C
	import mpu9250
	mpu = mpu9250.MPU9250(SoftI2C(scl = Pin(22), sda = Pin(21), freq = 400000))
	compass = mpu9250.Compass(mpu)
		
except Exception as e:
	print(e)
	
class LED:
	from machine import PWM
	
	def __init__(self, pin):
		self._pin = pin
		
	def setbrightness(self,val):
		self.PWM(Pin(self._pin)).duty(1023 - val)

	def setonoff(self,val):
		if(val == -1):
			Pin(self._pin,Pin.OUT).value(1 - Pin(self._pin).value())
		elif(val == 1):
			Pin(self._pin,Pin.OUT).value(0)
		elif(val == 0):
			Pin(self._pin,Pin.OUT).value(1)
			
	def getonoff(self):
		return not Pin(self._pin).value()
	
led1 = LED(0)
led2 = LED(5)

from neopixel import NeoPixel
rgb = NeoPixel(Pin(2), 2)


