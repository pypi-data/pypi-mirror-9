
import StringIO
import traceback
from datetime import datetime, timedelta
import pytz

#pip install suds
from suds.client import Client
import suds.transport as transport

#pip install requests
import requests


class IP01RequestsTransport(transport.Transport):
    def __init__(self, session=None):
        transport.Transport.__init__(self)
        self._timeout=5.0
        self._session = session or requests.Session()

    def open(self, request):
        # print "*****OPEN", request
        try:
            resp = self._session.get(request.url, verify=False, timeout=self._timeout)
            return StringIO.StringIO(resp.content)
        except:
            #print traceback.format_exc()
            raise transport.TransportError('open/requests error', 0)
 
    def send(self, request):
        # print "******SEND", request
        try:
            resp = self._session.post(
                request.url,
                data=request.message,
                headers=request.headers,
                verify=False,
                timeout=self._timeout
            )
            # print "RESP.HEADERS=", resp.headers
            # print "RESP.CONTENT=",resp.content
            return transport.Reply(
                resp.status_code,
                resp.headers,
                resp.content,
            )
        except:
            print traceback.format_exc()
            raise transport.TransportError('send/requests error', 0)


class IP01Sensor(object):
	def __init__(self, locationId, sensorId, tag):
		self._locationId=int(locationId)
		self._sensorId=int(sensorId)
		self._key='%d/%d' % (self._locationId, self._sensorId)
		self._tag=tag
		self._value=None
		self._dtStamp=None

	def updateValue(self, value, dt):
		if value is not None:
			self._value=value
			self._dtStamp=dt

	def age(self):
		try:
			if self._value is not None and self._dtStamp is not None:
				return (datetime.now(pytz.timezone('Europe/Zurich'))-self._dtStamp).total_seconds()
		except:
			return -1

	@property
	def key(self):
	    return self._key

	@property
	def locationId(self):
	    return self._locationId

	@property
	def sensorId(self):
	    return self._sensorId

	@property
	def value(self):
	    return self._value

	@property
	def tag(self):
	    return self._tag

	def idstr(self):
		return '%s/%s' % (self._key, self._tag)

	def __repr__(self):
		if self._value is not None:
			return '%s:%.01f (%ds)' % (self.idstr(), self.value, self.age())
		return '%s: None' % self.idstr()


class IP01(object):
	def __init__(self, server, port, username, password):
		self._server=server
		self._port=int(port)
		self._username=username
		self._password=password
		self._soap=None
		self._userId=0
		self._sensors={}
		self._indexLocations={}

	def url(self):
		return 'https://%s:%d/WebServiceProject/services/BusinessLogic?wsdl' % (self._server, self._port)

	def open(self):
		self._soap=None
		try:
			soap = Client(self.url(), transport=IP01RequestsTransport())

			loginParam=soap.factory.create('LoginParam')
			loginParam.login=self._username
			loginParam.password=self._password
			result=soap.service.login(loginParam)

			if result and result.isValid:
				self._userId=result.userId
				self._soap=soap
				return soap
		except:
			pass

	def soapDescribe(self):
		print self.open()

	def close(self):
		self._soap=None

	@property
	def soap(self):
	    return self._soap	

	def ping(self):
		try:
			if self.soap.service.hello() is not None:
				return True
			self.soap=None
		except:
			pass

	def sensors(self):
		return self._sensors.values()

	def locations(self):
		return self._indexLocations.keys()

	def computeSensorKey(self, locationId, sensorId):
		try:
			return '%d/%d' % (int(locationId), int(sensorId)) 
		except:
			pass

	def sensor(self, locationId, sensorId):
		skey=self.computeSensorKey(locationId, sensorId)
		try:
			return self._sensors[skey]
		except:
			pass

	def addSensor(self, locationId, sensorId, tag):
		s=self.sensor(locationId, sensorId)
		if s:
			return s
		s=IP01Sensor(locationId, sensorId, tag)
		self._sensors[s.key]=s
		try:
			self._indexLocations[s.locationId].append(s)
		except:
			self._indexLocations[s.locationId]=[s]
		return s

	def updateSensor(self, locationId, sensorId, value, dtStamp):
		s=self.sensor(locationId, sensorId)
		if s:
			s.updateValue(value, dtStamp)
			return s

	def retrieveSensorsFromLocation(self, locationId, tzstr='Europe/Zurich'):
		try:
			if self.ping() or self.open():
				print "RETR"
				params=self.soap.factory.create('GetSensorsFromLocationParam')
				params.userId=self._userId
				params.locationId=int(locationId)
				params.onlyProblematicSensors=False
				params.sensorId=0
				response=self.soap.service.getSensorsFromLocation(params)
				if response:
					# print response
					data=response.sensorLocations.split('|')
					tz=pytz.timezone(tzstr)
					records={}
					pos=8
					# print data
					rsize=13
					while True:
						rdata=data[pos:pos+rsize]
						pos+=rsize
						if len(rdata) != rsize:
							break

			            # print rdata
			 
						record={}
						try:
							sensorId=int(rdata[5].split('@')[1].encode('ascii','ignore'))
							tag=rdata[6].encode('ascii','ignore')
							sensor=self.addSensor(locationId, sensorId, tag)
							if sensor:
								tstamp=int(rdata[5].split('@')[0])
								dtStamp=datetime.fromtimestamp(tstamp/1000, tz)
								value=float(rdata[8])
								sensor.updateValue(value, dtStamp)
						except:
							# print rdata
							# print traceback.format_exc()
							pass
					return True
		except:
			pass

	def refresh(self):
		for locationId in self.locations():
			self.retrieveSensorsFromLocation(locationId)


if __name__ == '__main__':
    pass


