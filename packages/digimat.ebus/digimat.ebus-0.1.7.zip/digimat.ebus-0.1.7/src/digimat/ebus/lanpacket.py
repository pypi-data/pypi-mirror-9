import struct

LPHEADERSIZE=17
LPMAXDATASIZE=512

kLP_NOP=0xFF

class LP:
	def __init__(self, ptype=None, packetmanager=None):
		self._readpos=0
		self._data=bytearray()
		self._datasize=0
		self._synced=False
		self._packetmanager=packetmanager
		self._session=False
		if not ptype==None:
			self.create(ptype)

	def create(self, ptype, idRequest=0):
		header=bytearray(LPHEADERSIZE)
		header[0]=0xAA
		header[11]=ptype
		if idRequest:
			header[7]=idRequest&0xFF
			header[8]=idRequest>>8
		header[15]=0xA5
		self.writeData(header)
		self._datasize=0

	def erase(self):
		self._data=bytearray()
		self.rewind()

	def truncate(self):
		self._data=self._data[0:LPHEADERSIZE]
		self._synced=False
		self._datasize=0
		self.rewind()

	def openSession(self):
		self._session=True

	def closeSession(self):
		self._session=False

	def calcHeaderChecksum(self):
		chksum=0
		if len(self._data)>=LPHEADERSIZE-1:
			for b in self._data[0:LPHEADERSIZE-1]:
				chksum=chksum^b
		return chksum

	def calcHeader(self):
		size=len(self._data)-LPHEADERSIZE
		self._data[13]=size&0xFF
		self._data[14]=size>>8
		self._data[16]=self.calcHeaderChecksum()

	def checkHeader(self):
		try:
			if len(self._data)<LPHEADERSIZE:
				return False
			if self._data[0]!=0xAA or self._data[15]!=0xA5:
				return False
			if self.calcHeaderChecksum()!=self._data[16]:
				return False
			return True
		except:
			pass
		return False

	def extractDataSize(self):
		try:
			self._datasize=(self._data[14]<<8) | self._data[13]
			return self._datasize
		except:
			return 0

	def sync(self):
		while self._data:
			if self.checkHeader():
				size=self.extractDataSize()
				if len(self._data)<LPHEADERSIZE+size:
					return False
				self._synced=True
				return True
			print('OUTOFSYNC!')
			del self._data[0:1]
		return False

	def consumeData(self):
		if self._synced:
			self._data=self._data[LPHEADERSIZE+self._datasize:]
			self._datasize=0
			self.rewind()
			self._synced=False

	def writeData(self, data):
		size=len(data)
		if size:
			if len(self._data)+size>LPMAXDATASIZE:
				print("DEBUG LP presend")
				self.send()
			if len(self._data)+size<=LPMAXDATASIZE:
				self._data.extend(data)
				self._datasize=self._datasize+size
				return True
		print("LP:writeData() error!")
		return False

	def receiveData(self, data):
		size=len(data)
		if size:
			self._data.extend(data)
			return True
		print("LP:receiveData() error!")
		return False

	def getType(self):
		try:
			return self._data[11]
		except:
			return 0

	def dataToString(self, data):
		try:
			return ':'.join('%02X' % byte for byte in data)
		except:
			return ''

	def toString(self):
		str='LP[type={0}, S={1}, {2}]={3}'.format(self.getType(),
			self._datasize,
			self.dataToString(self._data[0:LPHEADERSIZE]),
			self.dataToString(self._data[LPHEADERSIZE:LPHEADERSIZE+self.extractDataSize()]))
		return str

	def dump(self):
		print self.toString()

	def getData(self, offset=0, size=0):
		if LPHEADERSIZE+offset+size<=LPHEADERSIZE+self._datasize:
			if size>0:
				return self._data[LPHEADERSIZE+offset:LPHEADERSIZE+offset+size]
			return self._data[LPHEADERSIZE+offset:LPHEADERSIZE+offset]
		return None

	def rewind(self):
		self._readpos=0

	def readData(self, size):
		data=self.getData(self._readpos, size)
		if data:
			self._readpos+=len(data)
		return data

	def readUP(self):
		data=self.readData(2)
		if data and len(data)==2:
			up=UP(self, data[0])
			#up.dump()
			size=data[1]
			if size==0:
				return up
			else:
				data=self.readData(size)
				if data and len(data)==size:
					up.addData(data)
					return up
			print('UP decoding error!')
			self.dump()
		return None

	def up(self, ptype=0):
		"""
		:rtype : UP
		"""
		return UP(self, ptype)

	def send(self, skipEmpty=True):
		if not self._session:
			if self._packetmanager:
				self._packetmanager.sendLP(self, skipEmpty)


#http://dabeaz.blogspot.com/2010/01/few-useful-bytearray-tricks.html
class UP:
	def __init__(self, lp, ptype=0):
		self._lp=lp
		self._readpos=0
		self._data=bytearray(struct.pack('BB', ptype, 0))

	def getType(self):
		return self._data[0]

	def setType(self, ptype):
		self._data[0]=ptype

	def erase(self):
		self._data=self._data[0:2]
		self.calcHeader()
		self.rewind()

	def getDataSize(self):
		try:
			size=len(self._data)
			return max(0,size-2)
		except:
			return 0

	def getFreeSize(self):
		return 255-len(self._data)+2

	def validateFreeSize(self, size):
		return size<self.getFreeSize()

	def calcHeader(self):
		size=len(self._data)-2
		self._data[1]=size

	def store(self):
		self.calcHeader()
		self._lp.writeData(self._data)

	def addData(self, data):
		if self.validateFreeSize(len(data)):
			self._data.extend(data)
		else:
			raise ValueError

	def writeStrField(self, str, size):
		if size>0:
			str=str[:size-1]
		self.addData(str+'\0'*(size-len(str)))

	def writeByte(self, value):
		self.addData(struct.pack('B', value))

	def writeBool(self, value):
		self.writeByte(bool(value))

	def writeWord(self, value):
		self.addData(struct.pack('<H', value))

	def writeFloat(self, value):
		self.addData(struct.pack('<f', value))

	def writeDouble(self, value):
		self.addData(struct.pack('<d', value))

	def toString(self):
		str='UP[type={0}, size={1}]={2}'.format(self.getType(),
			self.getDataSize(),
			self._lp.dataToString(self._data[2:]))
		return str

	def dump(self):
		print '  ' + self.toString()

	def getData(self, offset=0, size=0):
		if size>0:
			return self._data[2+offset:2+offset+size]
		return self._data[2+offset:2+offset]

	def rewind(self):
		self._readpos=0

	def readable(self, size=1):
		if self.getDataSize()-self._readpos>=size:
			return True
		return False

	def readData(self, size):
		if self.readable(size):
			data=self.getData(self._readpos, size)
			self._readpos+=size
			return data
		return None

	def readDataStr(self, size):
		#struct.unpack currently only support str
		return str(self.readData(size))

	def readStruct(self, format):
		size=struct.calcsize(format)
		data=self.readDataStr(size)
		if data:
			try:
				return struct.unpack(format, data)
			except:
				pass
		return None

	def readByte(self):
		if self.readable(1):
			return self.readStruct('B')[0]
		return 0

	def readBool(self):
		return bool(self.readByte())

	def readWord(self):
		if self.readable(2):
			return self.readStruct('<H')[0]
		return 0

	def readFloat(self):
		if self.readable(4):
			return self.readStruct('<f')[0]
		return 0

	def readDouble(self):
		if self.readable(4):
			return self.readStruct('<d')[0]
		return 0

	def readStrField(self, size):
		str=self.readDataStr(size).strip('\0')
		if str[-1]=='\0':
			str=str[:-1]
		return str


class PacketManager(object):
	def __init__(self):
		self._handlers={}
		self._lp=LP()

	def dispose(self):
		self.lpRx=None
		self._handlers=None

	def addHandler(self, lptype, uptype, handler):
		lphandler=self.lpHandler(lptype)
		if not lphandler:
			lphandler={}
			self._handlers[lptype]=lphandler
		lphandler[uptype]=handler

	def lpHandler(self, lptype):
		try:
			return self._handlers[lptype]
		except:
			pass
		return None

	def upHandler(self, lphandler, uptype):
		try:
			return lphandler[uptype]
		except:
			pass
		return None

	def receive(self, data):
		self._lp.receiveData(data)
		while self._lp.sync():
			self.onReceiveLP(self._lp)
			self._lp.consumeData()

	def sendLP(self, lp, skipEmpty=True):
		if not skipEmpty or lp._datasize>0:
			lp.calcHeader()
			#lp.dump()
			self.write(str(lp._data))
		lp.truncate()

	def write(self, data):
		raise NotImplementedError

	def onReceiveLP(self, lp):
		#lp.dump()
		lphandler=self.lpHandler(lp.getType())
		if lphandler:
			while 1:
				up=lp.readUP()
				if not up:
					break
				#up.dump()
				uphandler=self.upHandler(lphandler, up.getType())
				if uphandler:
					uphandler(up)
				else:
					print('unhandled UP type {0}'.format(up.getType()))
					#lp.dump()
					up.dump()
		else:
			# avoid connexion hangup by replying to nop messages
			if lp.getType()==kLP_NOP:
				self.sendLP(LP(kLP_NOP), False)
			else:
				#print('unhandled LP type {0}'.format(lp.getType()))
				#lp.dump()
				pass

