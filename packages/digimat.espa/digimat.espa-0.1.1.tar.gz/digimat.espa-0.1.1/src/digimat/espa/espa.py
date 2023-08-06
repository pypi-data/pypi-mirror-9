import time
import logging, logging.handlers

from threading import Thread
from threading import Event
from Queue import Queue

from notification import NotificationCallToPager, NotificationLinkTimeout

ESPA_CLIENT_ACTIVITY_TIMEOUT = 120

ESPA_CHAR_SOH   = '\x01'
ESPA_CHAR_STX   = '\x02'
ESPA_CHAR_ETX   = '\x03'
ESPA_CHAR_ENQ   = '\x05'
ESPA_CHAR_ACK   = '\x06'
ESPA_CHAR_NAK   = '\x15'
ESPA_CHAR_EOT   = '\x04'
ESPA_CHAR_US    = '\x1F'
ESPA_CHAR_RS    = '\x1E'


class CommunicationChannel(object):
    def __init__(self, link, logger):
        self._logger=logger
        link.setLogger(logger)
        self._link=link
        self._dead=False
        self._eventDead=Event()
        self._activityTimeout=time.time()+ESPA_CLIENT_ACTIVITY_TIMEOUT
        self._inbuf=None
        self.reset()

    @property
    def logger(self):
        return self._logger

    @property
    def name(self):
        return self._link.name

    def setDead(self, state=True):
        if state and not self._eventDead.isSet():
            self._eventDead.set()
        self._dead=bool(state)

    def isDeadEvent(self, reset=True):
        e=self._eventDead.isSet()
        if e:
            if reset:
                self._eventDead.clear()
            return True

    def dataToString(self, data):
        try:
            return ':'.join('%02X' % b for b in data)
        except:
            return ''

    def reset(self):
        self.logger.info('reset()')
        self._link.reset()
        self._inbuf=bytearray()

    def open(self):
        return self._link.open()

    def close(self):
        return self._link.close()

    def receive(self, size=0):
        if time.time()>self._activityTimeout:
            self.logger.warning('client activity timeout !')
            self.setDead(True)
            self.close()
            self._activityTimeout=time.time()+60

        bufsize=len(self._inbuf)

        if size==0 or size>bufsize:
            # fill the input buffer
            data=self._link.read()
            if data:
                self.logger.info('RX[%s]' % self.dataToString(data))
                self._inbuf.extend(data)
                self._activityTimeout=time.time()+ESPA_CLIENT_ACTIVITY_TIMEOUT

        try:
            if size>0:
                if bufsize>=size:
                    data=self._inbuf[:size]
                    self._inbuf=self._inbuf[size:]
                    return data
            else:
                data=self._inbuf
                self._inbuf=bytearray()
            return data
        except:
            pass

    def receiveByte(self):
        return self.receive(1)

    def send(self, data):
        if data:
            if type(data)==type(''):
                data=bytearray(data)
            self.logger.info('TX[%s]' % self.dataToString(data))
            return self._link.write(data)

    def sendByte(self, b):
        self.send(bytearray(b))

    def ack(self):
        self.logger.debug('>ACK')
        self.sendByte(ESPA_CHAR_ACK)

    def eot(self):
        self.logger.debug('>EOT')
        self.sendByte(ESPA_CHAR_EOT)

    def nak(self):
        self.logger.debug('>NAK')
        self.sendByte(ESPA_CHAR_NAK)


class MessageServer(object):
    def __init__(self, channel, logger):
        self._logger=logger
        self._channel=channel
        self._state=0
        self._stateTimeout=0
        self._inbuf=None
        self._bcc=0

    @property
    def logger(self):
        return self._logger

    def setTimeout(self, timeout):
        if timeout is not None:
            self._stateTimeout=time.time()+timeout

    def setState(self, state, timeout=None):
        self._state=state
        self.logger.debug('setMessageState(%d)' % state)
        self.setTimeout(timeout)

    def setNextState(self, timeout=None):
        self.setState(self._state+1, timeout)

    def abort(self):
        self.setState(-1)

    def waitByte(self, b):
        if b:
            data=self._channel.receiveByte()
            if data:
                if b==data:
                    return True
                # reject stream incoherence
                self.abort()

    def stateMachineManager(self):
        if self._state!=0 and time.time()>=self._stateTimeout:
            self.logger.warning('message state %d timeout!' % self._state)
            return False
        # --------------------------------------
        # reset
        if self._state==0:
            self.setNextState(3.0)
            self.logger.debug('WAITING FOR <SOH>')
        # --------------------------------------
        # wait for 'SOH'
        elif self._state==1:
            if self.waitByte(ESPA_CHAR_SOH):
                self._inbuf=bytearray()
                self._bcc=0
                self.setNextState(3.0)
                self.logger.debug('<SOH>OK, WAITING FOR BLOCK <DATA>+<ETX>')
        # --------------------------------------
        # wait for block <data>+<ETX>
        elif self._state==2:
            while True:
                b=self._channel.receiveByte()
                if b is not None:
                    break
                self._bcc ^= ord(b)
                if b==ESPA_CHAR_ETX:
                    self.logger.debug('<ETX>OK, WAITING FOR BCC')
                    self.setNextState()
                    break
                else:
                    self._inbuf.extend(b)
        # --------------------------------------
        # wait for 'BCC'
        elif self._state==3:
            b=self._channel.receiveByte()
            if b:
                if ord(b)==self._bcc:
                    self.logger.debug('<BCC>OK')
                    return self.decodeBuffer(self._inbuf)
                self.logger.error('<BCC>invalid')
                return False
        # --------------------------------------
        # bad state
        else:
            return False

    def decodeBuffer(self, buf):
        if buf:
            try:
                (header, body)=buf.split(ESPA_CHAR_STX)
                if header and body:
                    data={}
                    for record in body.split(ESPA_CHAR_RS):
                        if record:
                            (did, dvalue)=record.split(ESPA_CHAR_US)
                            data[str(did)]=str(dvalue)

                    notification=None
                    if header=='1':
                        notification=NotificationCallToPager(self._channel.name, self._data)
                    else:
                        # '2'=Status Information,
                        # '3'=Status Request,
                        # '4'=Call subscriber line
                        self.logger.warning('yet unsupported function [%s]' % header)

                    if notification:
                        if notification.validate():
                            return notification
            except:
                self.logger.exception('decodeBuffer()')


class Server(object):
    def __init__(self, link, contolEquipmentAddress='1', pageingSystemAddress='2', logServer='localhost', logLevel=logging.DEBUG):
        logger=logging.getLogger("ESPASERVER:%s" % link.name)
        logger.setLevel(logLevel)
        socketHandler = logging.handlers.SocketHandler(logServer,
            logging.handlers.DEFAULT_TCP_LOGGING_PORT)
        logger.addHandler(socketHandler)
        self._logger=logger

        self._controlEquipmentAddress=contolEquipmentAddress
        self._pageingSystemAddress=pageingSystemAddress

        self._channel=CommunicationChannel(link, self._logger)
        
        self._eventStop=Event()
        self._thread=Thread(target=self._manager)

        self._thread.daemon=True        
        self._state=0
        self._stateTimeout=0
        self._queueNotifications=Queue()

        self._messageServer=None
        self.onInit()

    @property
    def logger(self):
        return self._logger

    def start(self):
        self.logger.info('starting thread manager')
        self._thread.start()

    def stop(self):
        if not self._eventStop.isSet():
            self._eventStop.set()

    def setTimeout(self, timeout):
        if timeout is not None:
            self._stateTimeout=time.time()+timeout

    def setState(self, state, timeout=None):
        self._state=state
        self.logger.debug('setServerState(%d)' % state)
        self.setTimeout(timeout)

    def setNextState(self, timeout=None):
        self.setState(self._state+1, timeout)

    def resetState(self):
        self._channel.eot()
        self.setState(0)

    def waitByte(self, b):
        if b:
            data=self._channel.receiveByte()
            if data:
                if b==data:
                    return True
                # reject stream incoherence
                self.resetState()

    def onInit(self):
        pass

    def notify(self, notification):
        if notification:
            self._queueNotifications.put(notification)

    def stateMachineManager(self):
        # ESPA state machine
        if self._state!=0 and time.time()>=self._stateTimeout:
            self.logger.warning('state %d timeout!' % self._state)
            self.resetState()

        # --------------------------------------
        # reset
        if self._state==0:
            self._channel.reset()
            self._messageServer=None
            self.setNextState(60)
            self.logger.debug('WAITING FOR <1>')
        # --------------------------------------
        # wait for '1'
        elif self._state==1:
            if self.waitByte(self._controlEquipmentAddress):
                # from here we let 2500ms to get the initial
                # '1' + ENQ + '2' + ENQ sequence
                self.setNextState(2.5)
                self.logger.debug('<1>OK, WAITING FOR <ENQ>')
        # --------------------------------------
        # wait for 'ENQ'
        elif self._state==2:
            if self.waitByte(ESPA_CHAR_ENQ):
                self.setNextState()
                self.logger.debug('<ENQ>OK, WAITING FOR <2>')
        # --------------------------------------
        # wait for '2'
        elif self._state==3:
            if self.waitByte(self._pageingSystemAddress):
                self.setNextState()
                self.logger.debug('<2>OK, WAITING FOR <ENQ>')
        # --------------------------------------
        # wait for 'ENQ'
        elif self._state==4:
            if self.waitByte(ESPA_CHAR_ENQ):
                self._channel.ack()
                self._channel.setDead(False)
                self.setNextState(15.0)
                self.logger.debug('<ENQ>OK, WAITING FOR <MESSAGE>')
                self._messageServer=MessageServer(self._channel, self._logger)
        # --------------------------------------
        # manage espa message transaction
        elif self._state==5:
            if self._messageServer:
                notification=self._messageServer.stateMachineManager()

                # "notification" content is a bit unusual:
                # if content is something (a Notification) : job completed
                # if content is False : job terminated, but failed
                # if content is None : job is running (come back later)

                if notification:
                    self.logger.info(str(notification))
                    self.notify(notification)
                    self._channel.ack()
                    self.resetState()
                elif notification is False:
                    self._channel.sendByte(self._controlEquipmentAddress)
                    self._channel.nak()
                    self.resetState()
                else:
                    pass
        # --------------------------------------
        # bad state
        else:
            self.resetState()

    def _manager(self):
        self._channel.open()

        while not self._eventStop.isSet():
            try:
                self.stateMachineManager()
                if self._channel.isDeadEvent():
                    self.notify(NotificationLinkTimeout(self._channel.name))
                time.sleep(0.1)
            except:
                self.logger.exception('run()')
                self.stop()

        self._channel.close()

    def isRunning(self):
        return not self._eventStop.isSet()  

    def getNotification(self):
        try:
            return self._queueNotifications.get(False)
        except:
            pass      

    def waitForExit(self):
        self.stop()
        self.logger.debug("wait for thread termination")
        self._thread.join()
        self.logger.info("done")        


if __name__=='__main__':
    pass

