import xmlrpclib
from SimpleXMLRPCServer import SimpleXMLRPCServer
#import socket
from Queue import Queue
from threading import Thread
from threading import Event
from threading import RLock
import urlparse
import sys, logging, logging.handlers
import time
import re
import socket
import fcntl
import struct

import traceback

# for debug only
import pprint

#pip install requests
import requests

# Warning : slow request could be due to dns resolving.
# Adding hosts to /etc/hosts boost seriously the things ;)
# http://stackoverflow.com/questions/14504450/pythons-xmlrpc-extremely-slow-one-second-per-call
# http://www.answermysearches.com/xmlrpc-server-slow-in-python-how-to-fix/2140/
# --> basically, add "127.0.0.1 localhost" and "127.0.0.1 <pi-host-name>" to /etc/hosts

# CCU API
# https://groups.google.com/group/openhab/attach/a3f975a94f9e9b28/HM_XML-RPC_V1_502.pdf
# Chapter 5

# Useful AddOn for XML-RPC hacking
# http://www.homematic-inside.de/software/xml-api

class CCUEventHandler:
	def __init__(self, ccu):
		self._ccu=ccu

	def event(self, interface, address, key, value):
		self._ccu.onEvent(interface, address, key, value)
		return ''

	def listDevices(self, *args):
		# print ">LISTDEVICES"
		# for arg in args:
		# 	print arg
		# 	print "---"
		#pprint.pprint(args)
		return ''

	def newDevices(self, interface, devices):
		# print ">NEWDEVICES"
		# for device in devices:
		# 	print device
		# 	print "---"
		#pprint.pprint(args)
		return ''

	def newDevice(self, *args):
		#print ">NEWDEVICE"
		# for arg in args:
		# 	print arg
		#pprint.pprint(args)
		return ''

	# def shutdown(self, *args):
	# 	self._ccu._eventShutdown.set()
	# 	return ''



class CCUNotification(object):
	def __init__(self, domain, source, name, data={}):
		self._domain=domain
		self._name=name
		self._data=data

		self._source=source.lower()
		self._deviceId=self._source
		self._channel=0

		m=re.match('^([a-zA-Z0-9\-_]+):?([0-9])$', self._source)
		if m:
			self._deviceId=m.group(1)
			self._channel=int(m.group(2))

	@property
	def domain(self):
	    return self._domain

	@property
	def source(self):
	    return self._source

	@property
	def deviceId(self):
	    return self._deviceId

	@property
	def channel(self):
	    return self._channel

	def isSource(self, sources):
		try:
			if not isinstance(sources, (list, tuple)):
				sources=[sources]
			for source in sources:
				if source.lower()==self.source.lower():
					return True
		except:
			pass
		return False

	@property
	def name(self):
	    return self._name

	@property
	def key(self):
		try:
			return self._data['key']
		except:
			pass

	@property
	def value(self):
		try:
			return self._data['value']
		except:
			pass

	@property
	def state(self):
		return bool(self.value)

	def __getitem__(self, key):
		try:
			return self._data[key]
		except:
			pass

	def __setitem__(self, key, item):
		self._data[key]=item

	def dump(self):
		return 'NOTIFICATION-%s/%s(ch:%d)->%s(%s)' % (self.domain, self.deviceId, self.channel, self.name, self._data)

	def __repr__(self):
		return self.dump()

	def __str__(self):
		return self.dump()


class CCUNotificationDispatcher(object):
	def __init__(self):
		self._queue=Queue()
		self._event=Event()
		self._eventClose=Event()
		self._eventStamp=time.time()

	def post(self, notification):
		if notification and not self._eventClose.isSet():
			self._queue.put(notification)
			self._eventStamp=time.time()
			self._event.set()

	def getTimeSinceLastEvent(self):
		return time.time()-self._eventStamp

	def get(self):
		try:
			notification=self._queue.get(False)
			self._eventStamp=time.time()
			return notification
		except:
			self._event.clear()
		return None

	def sleep(self, delay):
		if not self._eventClose.isSet():
			return self._event.wait(delay)

	def waitForNotification(self, delay):
		if self.sleep(delay):
			return self.get()

	def kill(self):
		self._eventClose.set()
		self._event.set()



class CCUFlag(object):
	def __init__(self, ccu, name):
		self._lock=RLock()
		self._ccu=ccu
		self._name=name
		self._value=False
		self._stamp=0
		self._trigger1=0
		self._trigger0=0
		self.reset()

	@property
	def ccu(self):
	    return self._ccu

	@property
	def logger(self):
	    return self.ccu.logger

	@property
	def name(self):
	    return self._name

	def fid(self):
		return '%s' % (self.name)

	@property
	def value(self):
		with self._lock:
			return self._value
	@value.setter
	def value(self, value):
		with self._lock:
			value=bool(value)
			if value != self._value:
				self._value=value
				self._stamp=time.time()
				if self._value:
					self._trigger1=1
					self._trigger0=0
					self.logger.debug("FLAG(%s):0->1" % self.fid())
				else:
					self._trigger0=1
					self._trigger1=0
					self.logger.debug("FLAG(%s):1->0" % self.fid())

	def state(self):
		with self._lock:
			return bool(self.value)

	def isSet(self):
		with self._lock:
			return self.state()

	def isClear(self):
		with self._lock:
			return not self.state()

	def isPendingSet(self, clear=True):
		with self._lock:
			if self._trigger1:
				if clear:
					self._trigger1=0
				return True

	def isPendingSetAndStable(self, minAge, clear=True):
		with self._lock:
			if self.isPendingSet(False) and self.age()>=minAge:
				return self.isPendingSet()

	def isPendingClear(self, clear=True):
		with self._lock:
			if self._trigger0:
				if clear:
					self._trigger0=0
				return True

	def isPendingClearAndStable(self, minAge, clear=True):
		with self._lock:
			if self.isPendingClear(False) and self.age()>=minAge:
				return self.isPendingClear()

	def reset(self, value=0):
		with self._lock:
			self._trigger1=0
			self._trigger0=0
			self._value=bool(value)
			self._stamp=0

	def age(self):
		with self._lock:
			return time.time()-self._stamp

	def elapsed(self, delay):
		with self._lock:
			return self.age()>=delay


class CCUDeviceFlag(CCUFlag):
	def __init__(self, device, name):
		super(CCUDeviceFlag, self).__init__(device.ccu, 'DEVICE:%s:%s/%s' % (device.did, device.name, name))
		self._device=device

	@property
	def device(self):
	    return self._device

class CCUDevice(object):
	def __init__(self, ccu, did, name=''):
		self._lock=RLock()
		self._ccu=ccu
		self._did=did.lower()
		m=re.match('^([a-zA-Z0-9]+):([0-9])$', self._did)
		if m:
			self._did=m.group(1)
		self._nbchannel=1

		self._type='x'
		self._name=name
		self._enabled=True
		self._timeoutRefresh=0

		# common flags
		self._flagDead=self.flag('dead')
		self._flagSabotage=self.flag('sabotage')
		self._flagLowbat=self.flag('lowbat')

		self._ccu.registerDevice(self)
		self.onInit()
		self.manager()

	@property
	def ccu(self):
	    return self._ccu

	@property
	def logger(self):
	    return self.ccu.logger

	@property
	def did(self):
	    return self._did

	@property
	def nbchannel(self):
	    return self._nbchannel

	@property
	def type(self):
	    return self._type

	@property
	def name(self):
	    return self._name

	def enable(self, state=True):
		with self._lock:
			if state!= self._enabled:
				self._enabled=bool(state)
				self.logger.info("%s/%s:enable(%d)" % (self.type, self.did, self._enabled))

	def disable(self):
		with self._lock:
			self.enable(False)

	def isEnabled(self):
		with self._lock:
			return self._enabled

	def flag(self, name=''):
		with self._lock:
			return CCUDeviceFlag(self, name)

	def notify(self, notification):
		with self._lock:
			#self.logger.debug('trapped %s ccu notification [%s]' % (self.did, str(notification)))
			if notification.name=='event' and notification.deviceId==self.did:
				handler='onEvent_' + notification.key
				try:
					h=getattr(self, handler)
					#if h and callable(h) and hasattr(h, '_eventHandler'):
					if h and callable(h):
						try:
							return h(notification)
						except:
							self.logger.exception('notify()')
				except:
					pass

				self.logger.debug('%s/%s/%s:unhandled event [%s]' % (self.type, self.did, self.name, notification))

	def onInit(self):
		pass

	def isDead(self):
		with self._lock:
			return self._flagDead.isSet()

	def isAlive(self):
		with self._lock:
			return not self.isDead() and self.age()>=600

	def isPendingDead(self):
		with self._lock:
			return self._flagDead.isPendingSetAndStable(600)

	def isPendingDeadClear(self):
		with self._lock:
			return self._flagDead.isPendingClear()

	def isSabotage(self):
		with self._lock:
			return self._flagSabotage.isSet()

	def isPendingSabotage(self):
		with self._lock:
			return self._flagSabotage.isPendingSet()

	def isLowbat(self):
		with self._lock:
			return self._flagLowbat.isSet()

	def isPendingLowbat(self):
		with self._lock:
			return self._flagLowbat.isPendingSet()

	def onEvent_unreach(self, notification):
		with self._lock:
			self._flagDead.value=notification.state
			self.manager()

	def onEvent_install_test(self, notification):
		pass

	def onEvent_error(self, notification):
		with self._lock:
			self._flagSabotage.value=notification.state
			self.manager()

	def onEvent_lowbat(self, notification):
		with self._lock:
			self._flagLowbat.value=notification.state
			self.manager()

	def manager(self):
		with self._lock:
			if time.time()>=self._timeoutRefresh:
				self.onRefreshValues()
				self._timeoutRefresh=time.time()+180

	def getValue(self, channel, name):
		try:
			return self.ccu.rpc.getValue(self.channelAddress(channel), name)
		except:
			pass

	def setValue(self, channel, name, value):
		try:
			return self.ccu.rpc.setValue(self.channelAddress(channel), name, value)
		except:
			pass

	def onRefreshValues(self):
		pass

	def channelAddress(self, channel):
		return '%s:%d' % (self.did.upper(), channel)

	def getDeviceDescription(self, channel=1):
		response=self.ccu.rpc.getDeviceDescription(self.channelAddress(channel))
		self.logger.debug(response)
		return response

	def getParamsetDescription(self, channel=1, paramset='VALUES'):
		response=self.ccu.rpc.getParamsetDescription(self.channelAddress(channel), paramset.upper())
		self.logger.debug(response)
		# if response is not None:
		# 	for value in response:
		# 		print value
		# 		print response[value]
		# 		print "-"*60
		return response

	def getParamset(self, channel=1, paramset='VALUES'):
		response=self.ccu.rpc.getParamset(self.channelAddress(channel), paramset.upper())
		self.logger.debug(response)
		return response


class CCUVirtualChannels(CCUDevice):
	def __init__(self, ccu, did, name, nbchannels):
		super(CCUVirtualChannels, self).__init__(ccu, did, name)
		self._channels={}
		self._nbchannels=nbchannels
		for n in range(1, self._nbchannels+1):
			channel={}
			channel['shortpress']=self.flag('short-press-%d' % n)
			channel['longpress']=self.flag('short-press-%d' % n)
			self._channels[n]=channel

	@property
	def nbchannels(self):
	    return self._nbchannels

	def channel(self, channel):
		try:
			return self._channels[int(channel)]
		except:
			pass

	def onEvent_press_short(self, notification):
		c=self.channel(notification.channel)
		if c:
			flag=c['shortpress']
			flag.value=1

	def onEvent_press_long(self, notification):
		c=self.channel(notification.channel)
		if c:
			flag=c['longpress']
			flag.value=1

	def isPendingShortPress(self, channel):
		c=self.channel(channel)
		if c:
			flag=c['shortpress']
			if flag.isSet():
				flag.value=0
				return True

	def isPendingLongPress(self, channel):
		c=self.channel(channel)
		if c:
			flag=c['longpress']
			if flag.isSet():
				flag.value=0
				return True

	def isPendingPress(self, channel, shortPress=True):
		if shortPress:
			return self.isPendingShortPress(channel)
		return self.isPendingLongPress(channel)

	def __item__(self, key):
		return self.isPendingShortPress(key)



class CCURemote(CCUVirtualChannels):
	def __init__(self, ccu, did, name):
		super(CCURemote, self).__init__(ccu, did, name, 4)

	def isPendingButtonAlarm(self, shortPress=True):
		return self.isPendingPress(2, shortPress)

	def isPendingButtonAlarmAtHome(self, shortPress=True):
		return self.isPendingPress(1, shortPress)

	def isPendingButtonOff(self, shortPress=True):
		return self.isPendingPress(4, shortPress)

	def isPendingButtonLight(self, shortPress=True):
		return self.isPendingPress(3, shortPress)

	def isPendingButton(self, shortPress=True):
		for channel in self.nbchannels:
			if self.isPendingPress(channel, shortPress):
				return channel


class CCUAlarmDevice(CCUDevice):
	def __init__(self, ccu, did, name=''):
		super(CCUAlarmDevice, self).__init__(ccu, did, name)

	def onInit(self):
		super(CCUAlarmDevice, self).onInit()
		self._flagAlarm=self.flag('alarm')

	def isAlarm(self):
		with self._lock:
			if self._flagAlarm.isSet():
				if self.isEnabled():
					return True

	def isPendingAlarm(self):
		with self._lock:
			if self._flagAlarm.isPendingSet():
				if self.isEnabled():
					return True


class CCUInfraredDevice(CCUAlarmDevice):
	def onInit(self):
		super(CCUInfraredDevice, self).onInit()
		self._type='ir'
		self._brightness=None
		self._flagMotion=self.flag('motion')

	def isPendingMotion(self):
		with self._lock:
			return self._flagMotion.isPendingSet()

	@property
	def brightness(self):
		with self._lock:
		    return self._brightness

	def onEvent_brightness(self, notification):
		self._brightness=notification.value

	def onEvent_motion(self, notification):
		self.onChangeState(notification.value)

	def onChangeState(self, state):
		with self._lock:
			self._flagMotion.value=state
			self._flagAlarm.value=state

	# an IR device can't maintain state, so override default treatment
	def isAlarm(self):
		with self._lock:
			return False

	def onRefreshValues(self):
		try:
			self._brightness=self.getValue(channel, "BRIGHTNESS")
		except:
			pass

	def manager(self):
		super(CCUInfraredDevice, self).manager()
		if self._flagMotion.age()>3:
			self.onChangeState(0)


class CCUDoorDevice(CCUAlarmDevice):
	def onInit(self):
		super(CCUDoorDevice, self).onInit()
		self._type='door'
		self._flagOpen=self.flag('door')

	def isOpen(self):
		with self._lock:
			return self._flagOpen.isSet()

	def isClosed(self):
		with self._lock:
			return not self.isOpen()

	def isPendingOpen(self):
		with self._lock:
			return self._flagOpen.isPendingSet()

	def isPendingClose(self):
		with self._lock:
			return self._flagOpen.isPendingClear()

	def onChangeState(self, state):
		with self._lock:
			self._flagOpen.value=state
			self._flagAlarm.value=state

	def onEvent_state(self, notification):
		self.onChangeState(notification.value)

	def onRefreshValues(self):
		try:
			value=self.getValue(1, "STATE")
			self.onChangeState(value)
		except:
			pass

class CCURelayDevice(CCUDevice):
	def __init__(self, ccu, did, nbchannel, name=''):
		super(CCURelayDevice, self).__init__(ccu, did, name)
		self._type='switch'
		self._nbchannel=nbchannel
		self._flagsState=[]
		for channel in range(0, self._nbchannel):
			self._flagsState.append(self.flag('state%d' % channel))

	def onInit(self):
		super(CCURelayDevice, self).onInit()

	def getFlagState(self, channel):
		try:
			return self._flagsState[channel]
		except:
			pass

	def isOn(self, channel):
		with self._lock:
			try:
				return self.getFlagState(channel).isSet()
			except:
				pass

	def isOff(self, channel):
		with self._lock:
			return not self.isOn(channel)

	def isPendingOn(self, channel):
		with self._lock:
			try:
				return self.getFlagState(channel).isPendingSet()
			except:
				pass

	def isPendingOff(self, channel):
		with self._lock:
			try:
				return self.getFlagState(channel).isPendingClear()
			except:
				pass

	def onChangeState(self, channel, state):
		with self._lock:
			try:
				self.getFlagState(channel).value=state
			except:
				pass

	def onEvent_state(self, notification):
		self.onChangeState(notification.channel-1, notification.value)

	def onRefreshValues(self):
		try:
			for channel in range(0, self._nbchannel):
				value=self.getValue(channel+1, "STATE")
				self.onChangeState(channel, value)
		except:
			pass

	def setState(self, channel, state):
		self.setValue(channel+1, "STATE", bool(state))

	def on(self, channel):
		return self.setState(channel, 1)

	def off(self, channel):
		return self.setState(channel, 0)

	def onEvent_working(self, notification):
		pass


class CCUSingleRelayDevice(CCURelayDevice):
	def __init__(self, ccu, did, name=''):
		super(CCUSingleRelayDevice, self).__init__(ccu, did, 1, name)

	def isOn(self):
		return super(CCUSingleRelayDevice, self).isOn(0)

	def isOff(self):
		return super(CCUSingleRelayDevice, self).isOff(0)

	def isPendingOn(self):
		return super(CCUSingleRelayDevice, self).isPendingOn(0)

	def isPendingOff(self):
		return super(CCUSingleRelayDevice, self).isPendingOff(0)

	def setState(self, state):
		return super(CCUSingleRelayDevice, self).setState(0, state)

	def on(self):
		return self.setState(1)

	def off(self):
		return self.setState(0)


class CCUChimeDevice(CCUDevice):
	def __init__(self, ccu, did, name=''):
		super(CCUChimeDevice, self).__init__(ccu, did, name)
		self._type='chime'

	def flash(self):
		self.setValue(1, "STATE", True)

	def beep(self):
		self.setValue(2, "STATE", True)


class CCUDevices(object):
	def __init__(self, ccu):
		self._lock=RLock()
		self._ccu=ccu
		self._devices={}
		self._indexDeviceByName={}
		self._timeoutManager=0

	@property
	def ccu(self):
	    return self._ccu

	@property
	def logger(self):
	    return self.ccu.logger

	def getFromId(self, did):
		with self._lock:
			try:
				return self._devices[did]
			except:
				pass

	def getFromName(self, name):
		with self._lock:
			try:
				return self._indexDeviceByName[name]
			except:
				pass

	def register(self, device):
		with self._lock:
			try:
				if not self.getFromId(device.did):
					self._devices[device.did]=device
					self._indexDeviceByName[device.name]=device
					self.logger.info("Device %s[%s] registered" % (device.did, device.name))
				return device
			except:
				self.logger.exception('register()')

	def __getitem__(self, key):
		with self._lock:
			return self.getFromId(key)

	def __iter__(self):
		with self._lock:
			return self._devices.values().__iter__()

	def notify(self, notification):
		device=self.getFromId(notification.deviceId)
		if device:
			return device.notify(notification)
		else:
			self.logger.debug('UNMAPPED-EVENT:%s' % str(notification))

	def manager(self):
		if time.time()>=self._timeoutManager:
			self._timeoutManager=time.time()+0.1
			with self._lock:
				for device in self._devices.values():
					device.manager()



class CCUAlarmZoneFlag(CCUFlag):
	def __init__(self, zone, name):
		super(CCUAlarmZoneFlag, self).__init__(zone.ccu, 'ZONE:%s/%s' % (zone.name, name))
		self._zone=zone

	@property
	def zone(self):
	    return self._zone


class CCUDeviceManagedValue(object):
	def __init__(self, value=0.0, maxdepth=0):
		self._buffer=None
		self._stamp=0
		self._maxdepth=maxdepth
		self.reset()

	def reset(self, value=0.0):
		self._buffer=[]

	def store(self, value):
		if value is not None:
			self._buffer.append(value)
			self._stamp=time.time()
			if self._maxdepth>0:
				while self.size()>=self._maxdepth:
					self.pop()

	def elapsed(self, delay):
		if time.time()-self._stamp>=delay:
			return True

	def pop(self):
		try:
			return self._buffer.pop(0)
		except:
			pass

	def __iter__(self):
		return self._buffer.__iter__()

	def __getitem__(self, key):
		return self._buffer[key]

	def size(self):
		return len(self._buffer)

	def min(self):
		return min(self._buffer)

	def max(self):
		return min(self._buffer)

	def sum(self):
		return sum(self._buffer)

	def mean(self):
		count=len(self._buffer)
		if count>0:
			return float(self.sum())/float(count)
		return 0



class CCUAlarmZone(object):
	def __init__(self, ccu, name=''):
		self._lock=RLock()
		self._ccu=ccu
		self._name=name
		self._devices={}
		self._enabled=True
		self._flagAlarm=CCUAlarmZoneFlag(self, 'alarm')
		self._flagSabotage=CCUAlarmZoneFlag(self, 'sabotage')
		self._flagLowbat=CCUAlarmZoneFlag(self, 'lowbat')
		self._flagDead=CCUAlarmZoneFlag(self, 'dead')
		self._timeoutManager=0
		self._brightness=0

	@property
	def ccu(self):
	    return self._ccu

	@property
	def logger(self):
	    return self.ccu.logger

	@property
	def name(self):
	    return self._name

	def isMember(self, device):
		with self._lock:
			try:
				return self._devices[device.did]
			except:
				pass

	def addDevice(self, device):
		with self._lock:
			if not self.isMember(device):
				self._devices[device.did]=device
				self.logger.info('adding device [%s/%s] member to zone [%s]' % (device.did, device.name, self.name))
			return device

	def enable(self, state=True):
		with self._lock:
			for device in self._devices:
				device.enable(state)

	def disable(self, state):
		self.enable(False)

	def devices(self):
		with self._lock:
			return self._devices.values()

	def manager(self):
		if time.time()>=self._timeoutManager:
			alarm=False
			sabotage=False
			dead=False
			lowbat=False

			brightness=CCUDeviceManagedValue()

			for device in self.devices():
				if device.isPendingAlarm():
					alarm=True
				if device.isSabotage():
					dead=True
				if device.isDead():
					dead=True
				if device.isLowbat():
					lowbat=True
				try:
					# brightness property not always implemented, depending on device type
					value=device.brightness
					if value>0:
						brightness.store()
				except:
					pass

			if alarm:
				# raise only, manual reset via ackAlarm()
				self._flagAlarm.value=True

			self._flagSabotage.value=sabotage
			self._flagLowbat.value=lowbat
			self._flagDead.value=dead

			self._brightness=brightness.mean()

			self._timeoutManager=time.time()+0.2


	def isPendingAlarm(self):
		self.manager()
		return self._flagAlarm.isPendingSet()

	def isAlarm(self):
		self.manager()
		return self._flagAlarm.isSet()

	def ackAlarm(self):
		self._flagAlarm.clear()

	def isPendingSabotage(self):
		self.manager()
		return self._flagSabotage.isPendingSet()

	def isSabotage(self):
		self.manager()
		return self._flagSabotage.isSet()

	def isPendingLowbat(self):
		self.manager()
		return self._flagLowbat.isPendingSet()

	def isLowbat(self):
		self.manager()
		return self._flagLowbat.isSet()

	def isPendingDead(self):
		self.manager()
		return self._flagDead.isPendingSet()

	def isDead(self):
		self.manager()
		return self._flagDead.isSet()

	def isAlive(self):
		self.manager()
		return not self.isDead()

	def meanBightness(self):
		self.manager()
		return self._brightness

	def isBrightnessReportingDay(self):
		return self.meanBightness()>80

	def isBrightnessReportingNight(self):
		return self.meanBightness()>0 and self.meanBightness()<30


class CCU:
	def __init__(self, name, urlCCU, urlEventServer=None, logger=None):
		if not logger:
			logger=logging.getLogger("CCU")
			logger.setLevel(logging.DEBUG)
			ch = logging.StreamHandler(sys.stdout)
			ch.setLevel(logging.DEBUG)
			formatter = logging.Formatter('%(asctime)s:%(name)s::%(levelname)s::%(message)s')
			ch.setFormatter(formatter)
			logger.addHandler(ch)

		self._logger=logger
		self._notificationDispatcher=CCUNotificationDispatcher()
		self._eventStop=Event()
		#self._eventShutdown=Event()
		self._name=name

		self._devices=CCUDevices(self)

		self.logger.debug('creating XMLRPC client channel (%s)' % urlCCU)
		self._rpcClient=xmlrpclib.ServerProxy(urlCCU)

		if not urlEventServer:
			ip=self.guessIpAddress()
			if ip:
				urlEventServer='http://%s:8077' % ip

		self._urlEventServer=urlEventServer
		self._rpcEventServer=None
		self._timeoutRegisterEventServer=0

		self._vchannels=CCUVirtualChannels(self, 'bidcos-rf', 'ccu-vchannels', 50)

	@property
	def logger(self):
	    return self._logger

	@property
	def devices(self):
	    return self._devices

	@property
	def vchannels(self):
	    return self._vchannels

	def listDevices(self):
		response=self.rpc.listDevices()
		print response
		return response

	def setInstallMode(self, state=True):
		self.ccu.rpc.setInstallMode(boll(state))

	def getRssiInfo(self):
		response=self.rpc.rssiInfo()
		self.logger.debug(response)
		return response

	def listBidcosInterfaces(self):
		response=self.rpc.listBidcosInterfaces()
		self.logger.debug(response)
		return response


	def getInterfaceIpAddress(self, ifname='eth0'):
		try:
			s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
			return socket.inet_ntoa(fcntl.ioctl(s.fileno(),
				0x8915,  # SIOCGIFADDR
				struct.pack('256s', ifname[:15])
				)[20:24])
		except:
			self.logger.error('unable retrieve ip/%s address!' % ifname)

	def guessIpAddress(self):
		ip=self.getInterfaceIpAddress('eth0')
		if not ip:
			ip=self.getInterfaceIpAddress('en1')
		return ip

	@property
	def rpc(self):
		return self._rpcClient

	def notify(self, source, name, data):
	 	self._notificationDispatcher.post(CCUNotification('ccu', source, name, data))

	def registerDevice(self, device):
		return self._devices.register(device)

	def onEvent(self, interface, address, key, value):
		#self.logger.debug("EVENT[%s](%s=%s)" % (address, key, value))
		try:
			self.notify(address.lower(), 'event', {'key':key.lower(), 'value':value})
		except:
			pass

	def waitForNotification(self, delay):
		notification=self._notificationDispatcher.waitForNotification(delay)
		if notification:
			self._devices.notify(notification)
		if self._notificationDispatcher.getTimeSinceLastEvent()>180 and time.time()>=self._timeoutRegisterEventServer:
			self.logger.error('event notification timeout!')
			self._registerEventServer()
		return notification

	def _registerEventServer(self):
		try:
			self.logger.debug('registering local events server (%s) with CCU' % self._urlEventServer)
			self._rpcClient.init(self._urlEventServer, self._name)
		except:
			self.logger.exception('_registerEventServer()')
			self.logger.error("Unable to register XMLRPC event server (%s)!" % self._urlEventServer)

		self._timeoutRegisterEventServer=time.time()+15

	def _unregisterEventServer(self):
		self.logger.debug('unregistering local events server with CCU')
		try:
			self._rpcClient.init(self._urlEventServer)
		except:
			self.logger.error("Unable to unregister XMLRPC event server!")

	def start(self):
		try:
			self.logger.debug('creating XMLRPC server channel (%s)' % self._urlEventServer)
			url=urlparse.urlparse(self._urlEventServer)
			self._rpcEventServer=SimpleXMLRPCServer(('', url.port), logRequests=False)
			self._rpcEventServer.register_instance(CCUEventHandler(self))
			self._rpcEventServer.register_multicall_functions()
			#self._rpcEventServer.register_introspection_functions()
			self.logger.debug('XMLRPC server launched')

			self._threadXmlRpc=Thread(target=self._threadXmlRpcManager)
			#self._threadXmlRpc.daemon=True
			self._threadXmlRpc.start()
			self._registerEventServer()

			self._threadDevices=Thread(target=self._threadDevicesManager)
			#self._threadDevices.daemon=True
			self._threadDevices.start()

			return True

		except:
			self.logger.exception('start()')
			self.logger.error("Unable to launch XMLRPC server!")
			self.stop()


	def stop(self):
		if not self._eventStop.isSet():
			self.logger.info('stop request!')
			self._eventStop.set()
			self._notificationDispatcher.kill()
			self._unregisterEventServer()
			try:
				# send a dummy request to force shutdown http server
				url=urlparse.urlparse(self._urlEventServer)
				self.logger.debug('requesting local XMLRPC server shutdown...')

				#self._eventShutdown.isSet()
				r=requests.post('http://127.0.0.1:%d' % url.port, timeout=2.0)
				#client=xmlrpclib.ServerProxy('http://127.0.0.1:%d' % url.port)
				#client.shutdown()
			except:
				#traceback.print_exc(file=sys.stdout)
				pass

			self.logger.info('waiting for devices thread termination...')
			try:
				self._threadDevices.join()
			except:
				pass

			self.logger.info('waiting for XMLRPC server thread termination...')
			try:
				self._threadXmlRpc.join()
			except:
				pass

			self.logger.info('stop done.')


	def _threadXmlRpcManager(self):
		self.logger.info('XMLRPC server thread started')
		while not self._eventStop.isSet():
			try:
				self._rpcEventServer.handle_request()
			except:
				self.logger.error("exception occured while processing XMLRPC request!")
				#traceback.print_exc(file=sys.stdout)

		self.logger.info('XMLRPC server thread halted')

	def _threadDevicesManager(self):
		self.logger.info('devices manager thread started')
		while not self._eventStop.isSet():
			self._devices.manager()
			time.sleep(1)
		self.logger.info('devices manager thread halted')


if __name__ == '__main__':
	pass
