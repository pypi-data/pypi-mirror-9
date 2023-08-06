import time
import serial

# pyserial docs
# http://pyserial.sourceforge.net/pyserial_api.html

# list available ports
# python -m serial.tools.list_ports

# miniterm
# python -m serial.tools.miniterm <port name> [-h]


class Link(object):
    def __init__(self):
        self._logger=None
        self.setName('link')

    def setLogger(self, logger):
        self._logger=logger

    def setName(self, name):
        self._name=name

    @property
    def logger(self):
        return self._logger

    @property
    def name(self):
        return self._name

    def open(self):
        pass

    def reset(self):
        self.read()

    def close(self):
        pass

    def read(self):
        return None

    def write(self, data):
        return False


class LinkSerial(Link):
    def __init__(self, port, baudrate, parity=serial.PARITY_NONE, datasize=serial.EIGHTBITS, stopbits=serial.STOPBITS_ONE):
        super(LinkSerial, self).__init__()
        self.setName('RS(%s)' % port)
        self._serial=None
        self._port=port
        self._baudrate=baudrate
        self._parity=parity
        self._datasize=datasize
        self._stopbits=stopbits
        self._reopenTimeout=0

    def rtscts(self, enable=True):
        self._serial.rtscts=int(enable)

    def open(self):
        if self._serial:
            return True
        try:
            if time.time()>self._reopenTimeout:
                self._reopenTimeout=time.time()+15
                self.logger.info('open(%s)' % (self._port))

                s=serial.Serial(port=self._port,
                    baudrate=self._baudrate,
                    parity=self._parity,
                    stopbits=self._stopbits,
                    bytesize=self._datasize)

                s.timeout=0
                s.writeTimeout=0

                self._serial=s
                self.logger.info('port opened')

                return True
        except:
            #self.logger.exception('open()')
            self.logger.error('open() error')
            self._serial=None

    def close(self):
        try:
            self.logger.info('close()')
            #return self._serial.close()
        except:
            pass
        self._serial=None

    def read(self, size=255):
        try:
            if self.open():
                if size>0:
                    return bytearray(self._serial.read(size))
        except:
            self.logger.exception('read()')
            self.close()

    def write(self, data):
        try:
            if self.open():
                return self._serial.write(data)
        except:
            self.logger.exception('write()')
            self.close()


if __name__=='__main__':
    pass

