
import StringIO
import traceback
from datetime import datetime, timedelta

import sys, logging, logging.handlers

#pip install pytz
import pytz

#pip install suds
from suds.client import Client
import suds.transport as transport

#pip install requests
import requests


class IP01RequestsTransport(transport.Transport):
    def __init__(self, session=None, timeout=5.0, proxies={}, logger=None):
        transport.Transport.__init__(self)
        self._logger=logger
        self._timeout=timeout
        self._session = session or requests.Session()
        self._proxies=proxies

    @property
    def logger(self):
        return self._logger

    def open(self, request):
        # print "*****OPEN", request
        try:
            resp = self._session.get(request.url, verify=False, timeout=self._timeout, proxies=self._proxies)
            return StringIO.StringIO(resp.content)
        except:
            self.logger.exception('IP01RequestsTransport:open()')
            raise transport.TransportError('open/requests error', 0)

    def send(self, request):
        self.logger.debug('IP01RequestsTransport:send(%s)' % request)
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
            self.logger.exception('IP01RequestsTransport:send()')
            raise transport.TransportError('send/requests error', 0)


class IP01Sensor(object):
    def __init__(self, locationId, sensorId):
        self._locationId=int(locationId)
        self._sensorId=int(sensorId)
        self._key='%d/%d' % (self._locationId, self._sensorId)
        self._value=None
        self._dtStamp=None

    def updateValue(self, value, dt):
        if value is not None:
            self._dtStamp=dt
            if self._value != value:
                self._value=value
                return True

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

    def idstr(self):
        return self.key

    def valuestr(self):
        if self._value is not None:
            return '%.01f' % self.value
        return 'none'

    def __repr__(self):
        if self._value is not None:
            return '%s:%s (%ds)' % (self.idstr(), self.valuestr(), self.age())
        return '%s: None' % self.idstr()


class IP01(object):
    def __init__(self, host, username, password, timeout=5.0, logger=None):
        self._host=host
        self._timeout=timeout
        self._username=username
        self._password=password
        self._soap=None
        self._userId=0
        self._sensors={}
        self._indexLocations={}
        self._tzstr='Europe/Zurich'
        self._proxies={}

        if not logger:
            logger=logging.getLogger("IP01(%s)" % self._host)
            logger.setLevel(logging.DEBUG)
            ch = logging.StreamHandler(sys.stdout)
            ch.setLevel(logging.DEBUG)
            formatter = logging.Formatter('%(asctime)s:%(name)s::%(levelname)s::%(message)s')
            ch.setFormatter(formatter)
            logger.addHandler(ch)

        self._logger=logger

    @property
    def logger(self):
        return self._logger

    def url(self):
        return 'https://%s/WebServiceProject/services/BusinessLogic?wsdl' % self._host

    def setProxies(self, proxies={}):
        self._proxies=proxies

    def open(self):
        self._soap=None
        try:
            soap = Client(self.url(), transport=IP01RequestsTransport(None, self._timeout, self._proxies, self._logger))

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

    def setTimeZone(self, tzstr):
        self._tzstr=tzstr

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

    def addSensor(self, locationId, sensorId):
        s=self.sensor(locationId, sensorId)
        if s:
            return s
        s=IP01Sensor(locationId, sensorId)
        self._sensors[s.key]=s

        self.logger.debug('adding sensor %s' % s.key)

        try:
            self._indexLocations[s.locationId].append(s)
        except:
            self._indexLocations[s.locationId]=[s]
        return s

    def updateSensor(self, locationId, sensorId, value, dtStamp):
        s=self.sensor(locationId, sensorId)
        if s:
            if s.updateValue(value, dtStamp):
                self.logger.info('sensor %s updated (%s)' % (s.idstr(), s.valuestr()))
            return s

    def importSensorsFromLocation(self, locationId, autoCreate=False):
        try:
            if self.ping() or self.open():
                params=self.soap.factory.create('GetSensorsFromLocationParam')
                params.userId=self._userId
                params.locationId=int(locationId)
                params.onlyProblematicSensors=False
                params.sensorId=0
                response=self.soap.service.getSensorsFromLocation(params)
                if response:
                    #print response
                    data=response.sensorLocations.split('|')
                    tz=pytz.timezone(self._tzstr)
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
                            # tag=rdata[6].encode('ascii','ignore')

                            tstamp=int(rdata[5].split('@')[0])
                            dtStamp=datetime.fromtimestamp(tstamp/1000, tz)
                            value=float(rdata[8])

                            if autoCreate:
                                sensor=self.addSensor(locationId, sensorId)

                            self.updateSensor(locationId, sensorId, value, dtStamp)
                        except:
                            #self.logger.exception('importSensorsFromLocation()')
                            pass
                    return True
        except:
            pass

    def read(self):
        for locationId in self.locations():
            self.importSensorsFromLocation(locationId)


if __name__ == '__main__':
    pass

