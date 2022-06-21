from machine import Pin, SoftI2C
from micropython import const
import ustruct
import time
import gc

_DISPLAY_BLINK_CMD 			= const(0x80)
_DISPLAY_BLINK_DISPLAYON 	= const(0x01)
_DISPLAY_CMD_BRIGHTNESS 	= const(0xE0)
_DISPLAY_OSCILATOR_ON 		= const(0x21)

class Image:
	def __init__(self,str=""):
		if str.find(',') != -1:
			rows = [] 
			for row in str.split(','):
				new_row = ['0'] * 16 
				for hex in row:
					idx = int(hex, 16)
					new_row[idx] = '1'
				rows.append(''.join(new_row))
			self.str = ':'.join(rows)
		else:
			self.str = str

	def __add__(self,other):
		img = Image()
		l1 = self.str.split(':')
		l2 = other.str.split(':')
		l = []
		s = ""
		for i in range(8):
			for j in range(16):
				if l2[i][j]>l1[i][j]:
					s += l2[i][j]
				else:
					s += l1[i][j]
			l.append(s)
			s = ""
		img.str = ":".join(l)
		return img

	def __sub__(self,other):
		img = Image()
		l1 = self.str.split(':')
		l2 = other.str.split(':')
		l = []
		s = ""
		for i in range(8):
			for j in range(16):
				if l2[i][j]=='1' and l1[i][j]=='1':
					s += '0'

				else:
					s += l1[i][j]
			l.append(s)
			s = ""
		img.str = ":".join(l)
		return img

	def height(self):
		start=-1
		check_start=0
		check_end=7
		end=-1
		l = self.str.split(':')
		while start==-1:
			for i in range(16):
				if l[check_start][i] == '1':
					start=check_start
			check_start=check_start+1
			if check_start>7:
				return 0
				break
		while end==-1:
			for i in range(16):
				if l[check_end][i] == '1':
					end=check_end
			check_end=check_end-1
		return end-start+1 

	def width(self):
		start=-1
		check_start=0
		check_end=15
		end=-1
		l = self.str.split(':')
		while start==-1:
			for i in range(8):
				if l[i][check_start] == '1':
					start=check_start
			check_start=check_start+1
			if check_start>15:
				return 0
				break
		while end==-1:
			for i in range(8):
				if l[i][check_end] == '1':
					end=check_end
			check_end=check_end-1
		return end-start+1      

	def copy(self):
		return self   

	def invert(self):
		l = self.str.split(':')
		a=''
		for i in range(8):
				for j in range(16):
					if l[i][j] == '1':
						a=a+'0'
					else:
						a=a+'1'
				if i<7:
					a=a+':'

		return Image(a)    
	
	def shift_up(self, num):
		if num<0:
			return self.shift_down(-num)
		elif num>7:
			return Image(',,,,,,,')
		else:    
			l = self.str.split(':')
			a=''
			for i in range(8):
				if i<8-num:
					a=a+l[i+num]
				else:
					a=a+'0000000000000000'    
				if i<7:
					a=a+':'    
			b=Image(a)          
			return b

	def shift_down(self, num):
		if num<0:
			return self.shift_up(-num)
		elif num>7:
			return Image(',,,,,,,')
		else:    
			l = self.str.split(':')
			a=''
			for i in range(8):
				if i<num:
					a=a+'0000000000000000'
				else:
					a=a+l[i-num]    
				if i<7:
					a=a+':'    
			b=Image(a)          
			return b        

	def shift_left(self, num):
		if num<0:
			return self.shift_right(-num)
		elif num>15:
			return Image(',,,,,,,')
		else:    
			l = self.str.split(':')
			a=''
			for i in range(8):
				for j in range(16-num):
					a=a+l[i][j+num]
				for j in range(num):
					a=a+'0'                
				if i<7:
					a=a+':'    
			b=Image(a)          
			return b

	def shift_right(self, num):
		if num<0:
			return self.shift_left(-num)
		elif num>15:
			return Image(',,,,,,,')
		else:    
			l = self.str.split(':')
			a=''
			for i in range(8):
				for j in range(num):
					a=a+'0' 
				for j in range(num,16):
					a=a+l[i][j-num]                               
				if i<7:
					a=a+':'    
			b=Image(a)          
			return b        

class BitmapFont:
	def __init__(self, width, height, pixel):
		self._width = width
		self._height = height
		self._pixel = pixel
		self._font_code=b'\x05\x08\x00\x00\x00\x00\x00>[O[>>kOk>\x1c>|>\x1c\x18<~<\x18\x1cW}W\x1c\x1c^\x7f^\x1c\x00\x18<\x18\x00\xff\xe7\xc3\xe7\xff\x00\x18$\x18\x00\xff\xe7\xdb\xe7\xff0H:\x06\x0e&)y)&@\x7f\x05\x05\x07@\x7f\x05%?Z<\xe7<Z\x7f>\x1c\x1c\x08\x08\x1c\x1c>\x7f\x14"\x7f"\x14__\x00__\x06\t\x7f\x01\x7f\x00f\x89\x95j`````\x94\xa2\xff\xa2\x94\x08\x04~\x04\x08\x10 ~ \x10\x08\x08*\x1c\x08\x08\x1c*\x08\x08\x1e\x10\x10\x10\x10\x0c\x1e\x0c\x1e\x0c08>80\x06\x0e>\x0e\x06\x00\x00\x00\x00\x00\x00\x00_\x00\x00\x00\x07\x00\x07\x00\x14\x7f\x14\x7f\x14$*\x7f*\x12#\x13\x08db6IV P\x00\x08\x07\x03\x00\x00\x1c"A\x00\x00A"\x1c\x00*\x1c\x7f\x1c*\x08\x08>\x08\x08\x00\x80p0\x00\x08\x08\x08\x08\x08\x00\x00``\x00 \x10\x08\x04\x02>QIE>\x00B\x7f@\x00rIIIF!AIM3\x18\x14\x12\x7f\x10\'EEE9<JII1A!\x11\t\x076III6FII)\x1e\x00\x00\x14\x00\x00\x00@4\x00\x00\x00\x08\x14"A\x14\x14\x14\x14\x14\x00A"\x14\x08\x02\x01Y\t\x06>A]YN|\x12\x11\x12|\x7fIII6>AAA"\x7fAAA>\x7fIIIA\x7f\t\t\t\x01>AAQs\x7f\x08\x08\x08\x7f\x00A\x7fA\x00 @A?\x01\x7f\x08\x14"A\x7f@@@@\x7f\x02\x1c\x02\x7f\x7f\x04\x08\x10\x7f>AAA>\x7f\t\t\t\x06>AQ!^\x7f\t\x19)F&III2\x03\x01\x7f\x01\x03?@@@?\x1f @ \x1f?@8@?c\x14\x08\x14c\x03\x04x\x04\x03aYIMC\x00\x7fAAA\x02\x04\x08\x10 \x00AAA\x7f\x04\x02\x01\x02\x04@@@@@\x00\x03\x07\x08\x00 TTx@\x7f(DD88DDD(8DD(\x7f8TTT\x18\x00\x08~\t\x02\x18\xa4\xa4\x9cx\x7f\x08\x04\x04x\x00D}@\x00 @@=\x00\x7f\x10(D\x00\x00A\x7f@\x00|\x04x\x04x|\x08\x04\x04x8DDD8\xfc\x18$$\x18\x18$$\x18\xfc|\x08\x04\x04\x08HTTT$\x04\x04?D$<@@ |\x1c @ \x1c<@0@<D(\x10(DL\x90\x90\x90|DdTLD\x00\x086A\x00\x00\x00w\x00\x00\x00A6\x08\x00\x02\x01\x02\x04\x02<&#&<\x1e\xa1\xa1a\x12:@@ z8TTUY!UUyA"TTxB!UTx@ TUy@\x0c\x1eRr\x129UUUY9TTTY9UTTX\x00\x00E|A\x00\x02E}B\x00\x01E|@}\x12\x11\x12}\xf0(%(\xf0|TUE\x00 TT|T|\n\t\x7fI2III2:DDD:2JHH0:AA!z:B@ x\x00\x9d\xa0\xa0}=BBB==@@@=<$\xff$$H~ICf+/\xfc/+\xff\t)\xf6 \xc0\x88~\t\x03 TTyA\x00\x00D}A0HHJ28@@"z\x00z\n\nr}\r\x191}&))/(&)))&0HM@ 8\x08\x08\x08\x08\x08\x08\x08\x088/\x10\xc8\xac\xba/\x10(4\xfa\x00\x00{\x00\x00\x08\x14*\x14""\x14*\x14\x08U\x00U\x00U\xaaU\xaaU\xaa\xffU\xffU\xff\x00\x00\x00\xff\x00\x10\x10\x10\xff\x00\x14\x14\x14\xff\x00\x10\x10\xff\x00\xff\x10\x10\xf0\x10\xf0\x14\x14\x14\xfc\x00\x14\x14\xf7\x00\xff\x00\x00\xff\x00\xff\x14\x14\xf4\x04\xfc\x14\x14\x17\x10\x1f\x10\x10\x1f\x10\x1f\x14\x14\x14\x1f\x00\x10\x10\x10\xf0\x00\x00\x00\x00\x1f\x10\x10\x10\x10\x1f\x10\x10\x10\x10\xf0\x10\x00\x00\x00\xff\x10\x10\x10\x10\x10\x10\x10\x10\x10\xff\x10\x00\x00\x00\xff\x14\x00\x00\xff\x00\xff\x00\x00\x1f\x10\x17\x00\x00\xfc\x04\xf4\x14\x14\x17\x10\x17\x14\x14\xf4\x04\xf4\x00\x00\xff\x00\xf7\x14\x14\x14\x14\x14\x14\x14\xf7\x00\xf7\x14\x14\x14\x17\x14\x10\x10\x1f\x10\x1f\x14\x14\x14\xf4\x14\x10\x10\xf0\x10\xf0\x00\x00\x1f\x10\x1f\x00\x00\x00\x1f\x14\x00\x00\x00\xfc\x14\x00\x00\xf0\x10\xf0\x10\x10\xff\x10\xff\x14\x14\x14\xff\x14\x10\x10\x10\x1f\x00\x00\x00\x00\xf0\x10\xff\xff\xff\xff\xff\xf0\xf0\xf0\xf0\xf0\xff\xff\xff\x00\x00\x00\x00\x00\xff\xff\x0f\x0f\x0f\x0f\x0f8DD8D\xfcJJJ4~\x02\x02\x06\x06\x02~\x02~\x02cUIAc8DD<\x04@~ \x1e \x06\x02~\x02\x02\x99\xa5\xe7\xa5\x99\x1c*I*\x1cLr\x01rL0JMM00HxH0\xbcbZF=>III\x00~\x01\x01\x01~*****DD_DD@QJD@@DJQ@\x00\x00\xff\x01\x03\xe0\x80\xff\x00\x00\x08\x08kk\x086\x126$6\x06\x0f\t\x0f\x06\x00\x00\x18\x18\x00\x00\x00\x10\x10\x000@\xff\x01\x01\x00\x1f\x01\x01\x1e\x00\x19\x1d\x17\x12\x00<<<<\x00\x00\x00\x00\x00'
	
	def init(self):
		self._font_width, self._font_height = ustruct.unpack('BB', b'\x05\x08')

	def __enter__(self):
		self.init()
		return self

	def __exit__(self, exception_type, exception_value, traceback):
		pass

	def draw_char(self, ch, x, y):
		# Don't draw the character if it will be clipped off the visible area.
		if x < -self._font_width or x >= self._width or \
		   y < -self._font_height or y >= self._height:
			return
		# Go through each column of the character.
		for char_x in range(self._font_width):            
			# Grab the byte for the current column of font data.
			chcode=bytes([self._font_code[(2 + (ord(ch) * self._font_width) + char_x)]]) 
			line = ustruct.unpack('B', chcode)[0]
			# Go through each row in the column byte.
			for char_y in range(self._font_height):
				# Draw a pixel for each bit that's flipped on.
				if (line >> char_y) & 0x1:
					self._pixel(x + char_x, y + char_y, 1)

	def text(self, text, x, y):
		# Draw the specified text at the specified location.
		for i in range(len(text)):
			self.draw_char(text[i], x + (i * (self._font_width + 1)), y)
	def width(self, text):
		# Return the pixel width of the specified text message.
		return len(text) * (self._font_width + 1)


class HT16K33:
	"""The base class for all Display-based backpacks and wings."""
	def __init__(self, i2c, address=0x70):
		self._i2c = i2c
		self._address = address
		self._buffer = bytearray(16)
		self._write_cmd(_DISPLAY_OSCILATOR_ON)
		self.blink_rate(0)
		self.brightness(5)
		self.fill(0)
		self.show()
		
	def _write_cmd(self, val):
		"""Send a command."""
		self._i2c.writeto(self._address,val.to_bytes(1, 'little'))

	def blink_rate(self, rate=None):
		"""Get or set the blink rate."""
		if rate is None:
			return self._blink_rate
		rate = rate & 0x02
		self._blink_rate = rate
		self._write_cmd(_DISPLAY_BLINK_CMD |
						_DISPLAY_BLINK_DISPLAYON | rate << 1)

	def brightness(self, brightness):
		"""Get or set the brightness."""
		if brightness is None:
			return self._brightness
		brightness = brightness & 0x0F
		self._brightness = brightness
		self._write_cmd(_DISPLAY_CMD_BRIGHTNESS | brightness)

	def show(self):
		self._i2c.writeto_mem(self._address, 0x00, self._buffer)

	def fill(self, color):
		"""Fill the display with given color."""
		fill = 0xff if color else 0x00
		for i in range(16):
			self._buffer[i] = fill

	def pixel(self, x, y, color=None):
		"""Set a single pixel in the frame buffer to specified color."""
		if not 0 <= x <= 15:
			return None
		if not 0 <= y <= 7:
			return None	
		addr = 2 * y + x // 8
		mask = 1 << x % 8
		if color is None:
			return bool(self._buffer[addr] & mask)
		if color:
			self._buffer[addr] |= mask
		else:
			self._buffer[addr] &= ~mask



i2c = SoftI2C(scl=Pin(22), sda=Pin(21), freq=400000)
display = HT16K33(i2c)
gc.collect()

def set_pixel( x, y, flag):
	display.pixel(x, y, flag)
	display.show()

def get_pixel(x, y):
	return display.pixel(x, y)
		
def set_brightness(brightness):
	display.brightness(brightness)
	display.show()

def blink_rate(rate):
	return display.blink_rate(rate)
	
def get_brightness():
	return display.brightness(None)
	
def clear():
	display.fill(0)
	display.show()

def show(data, delay=200):        
	if type(data)==type(Image.HEART):
		display.fill(0)
		l = data.str.split(':')
		for i in range(8):
			for j in range(16):
				if l[i][j] == '1':
					display.pixel(j, i, 1)
		display.show()
	else:
		data=str(data)
		with BitmapFont(16, 8, display.pixel) as bf:
			for msg in data:
				display.fill(0)
				bf.draw_char(msg, 5, 0) 
				display.show()
				time.sleep_ms(delay)    

def scroll(data, speed=120):
	if type(data)==str:
		with BitmapFont(16, 8, display.pixel) as bf:           
			for i in range(bf.width(data)+16):
				x=-i+16
				display.fill(0)
				bf.text(data, x, 0)
				display.show()
				time.sleep_ms(speed)
	else:    
		show(data)
    
def get_screenimage():
	a=''
	for i in range(8):
		for j in range(16):
			if display.pixel(j, i) ==1:
				a=a+'1'
			else:
				a=a+'0'
		if i<7:
			a=a+':'				
	return Image(a)


def showstatic(data):
	display.fill(0)
	data=str(data)
	with BitmapFont(16, 8, display.pixel) as bf:  
		x=(16-bf.width(data))//2
		bf.text(data, x, 0)
		display.show()

Image.HEART=Image('59,45689a,3456789ab,3456789ab,456789a,56789,678,7')
Image.HEART_SMALL=Image(',59,45689a,456789a,56789,678,7,')
Image.HAPPY=Image(',,34bc,34bc,,5a,69,78')
Image.SAD=Image(',,345abc,2d,,78,69,5a')
Image.SMILE=Image(',34bc,25ad,,,5a,69,78')
Image.SILLY=Image(',34bc,25ad,34bc,,6789,69,78')
Image.FABULOUS=Image('345abc,269d,234569abcd,,,56789a,5a,6789')
Image.SURPRISED=Image(',7,7,7,7,7,,7')
Image.ASLEEP=Image(',,2345abcd,,,6789,5a,6789')
Image.ANGRY=Image('269d,35ac,4b,,78,69,5a,4b')
Image.CONFUSED=Image(',678,59,9,8,7,,7')
Image.NO=Image(',49,58,67,67,58,49,')
Image.YES=Image(',c,b,a,49,58,67,')
Image.LEFT_ARROW=Image(',5,4,3,2456789abcd,3,4,5')
Image.RIGHT_ARROW=Image(',a,b,c,23456789abd,c,b,a')
Image.DRESS=Image('59,456789a,5689,678,579,468a,3579b,456789a')
Image.TRANSFORMERS=Image(',7,5689,579,579,68,68,59')
Image.SCISSORS=Image('5b,56ab,679a,789,8,679a,579b,6a')
Image.EXIT=Image('ab,89a,79ab,69cd,8a,68b,8c,d')
Image.TREE=Image('7,678,56789,456789a,3456789ab,7,7,7')
Image.PACMAN=Image('456789,34a,2369,28,239,34a,456789,')
Image.TARGET=Image(',,789,6a,68a,6a,789,')
Image.TSHIRT=Image('5a,46789b,3c,45ab,5a,5a,5a,56789a')
Image.ROLLERSKATE=Image('4567,47,4789a,4b,456789ab,35ac,345abc,')
Image.DUCK=Image('567,478,38,23458,589abcde,5d,5c,56789ab')
Image.HOUSE=Image('23456789abcd,12de,01ef,256789ad,25ad,257ad,25ad,25ad')
Image.TORTOISE=Image('78,578a,56789a,56789a,56789a,6789,5a,')
Image.BUTTERFLY=Image(',56ab,479c,56789ab,789,68a,579b,56ab')
Image.STICKFIGURE=Image('7,68,7,678,579,7,68,59')
Image.GHOST=Image('56789,4579a,4579a,456789a,4579a,468a,456789ab,456789abc')
Image.PITCHFORK=Image('bcdef,a,a,0123456789abcdef,a,a,bcdef,')
Image.MUSIC_QUAVERS=Image(',,349af,234589abe,14567abcd,056bc,,')
Image.MUSIC_QUAVER=Image('1234567,08,0123456789ab,9abc,89abcd,89abcd,9abcd,abc')
Image.MUSIC_CROTCHET=Image(',0123456789ab,9abc,89abcd,89abcd,9abcd,abc,')
Image.COW=Image('3,1234,13456789a,123456789ab,123456789acd,459ae,459a,459a')
Image.RABBIT=Image('6789abcd,123456e,08ce,12345abce,08ce,123456e,6789abcd,')
Image.SQUARE_SMALL=Image(',,6789,69,69,6789,,')
Image.SQUARE=Image('456789ab,4b,4b,4b,4b,4b,4b,456789ab')
Image.DIAMOND_SMALL=Image(',,678,579,68,7,,')
Image.DIAMOND=Image('456789a,3468ab,2356789bc,34678ab,4579a,5689,678,7')
Image.CHESSBOARD=Image(',3456789abcd,3579bd,3456789abcd,3579bd,3456789abcd,3579bd,3456789abcd')
Image.TRIANGLE_LEFT=Image(',8,78,678,5678,678,78,8')
Image.TRIANGLE=Image(',78,6789,56789a,456789ab,3456789abc,23456789abcd,')
Image.SNAKE=Image('9ab,9b,9ab,456789,3456789,234,123,')
Image.UMBRELLA=Image('7,56789,456789a,3456789ab,7,7,79,789')
Image.SKULL=Image('56789,47a,37b,345689ab,456789a,59,579,678')
Image.GIRAFFE=Image('78,789,7,7,7,4567,47,47')
Image.SWORD=Image(',4,45,23456789abc,23456789abc,45,4,')
gc.collect()