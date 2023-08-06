from . import Sensor, SensorError

import time
import serial

__all__ = ['SerialSensor', 'ConnectionClosedError', 'CorruptDataError']


class ConnectionClosedError(SensorError):
    """
    This error should be thrown when the connection to a sensor is unexpectedly
    closed.
    """
    pass


class CorruptDataError(SensorError):
    """
    This error should be thrown when the data read from the sensor is determined
    to be corrupt.

    :param sensor: the :class:`~sensorlib.Sensor` for which this exception
        occurred
    :param data: the data received that was determined to be corrupt
    """
    def __init__(self, sensor, data):
        super(CorruptDataError, self).__init__(sensor)
        self.data = data


class SerialSensor(Sensor, serial.Serial):
    """
    Class for reading from a serial sensor

    :param list measurements: A list of names of measurements that this sensor
        takes in the order they are returned by the sensor itself
    :param str serial_port: the serial port of the sensor (e.g. '/dev/ttyUSB0')
    :param read_command: a string to be sent to the sensor to perform a read
    :param int wait_time: time to wait after sending the read command before
        trying to read the data (in milliseconds)
    :param **kwargs: additional arguments to be passed to the constuctor for
        :class:`serial.Serial`
    """
    def __init__(self, measurements, serial_port, read_command='R\r',
                 wait_time=1000, **kwargs):
        Sensor.__init__(self, measurements)
        serial.Serial.__init__(self, port=serial_port, **kwargs)
        self.read_command = read_command
        self.wait_time = wait_time

        attempted_reads = 0
        successful_reads = 0
        # Try to read until 2 valid reads are performed in a row.
        while successful_reads < 2:
            try:
                self.measure()
            except (CorruptDataError, ValueError) as e:
                successful_reads = 0
                # After 10 attempts, stop silencing errors
                if attempted_reads >= 10:
                    raise e
            else:
                successful_reads += 1
            finally:
                attempted_reads += 1

    def read_string(self):
        """
        Reads from the input buffer and parses the result as a string
        """
        if not self.isOpen():
            raise ConnectionClosedError(self)
        string = self.read(self.inWaiting()).decode('ascii')
        # Cut out any data after the first carriage return
        cr = string.find('\r')
        if cr != -1:
            string = string[:cr]
        return string.replace('\r', '').replace('\n', '')

    def read_values(self):
        """
        Reads from the input buffer and parses the result as a list of floats
        """
        string = self.read_string()
        values = [float(i) for i in string.split(',')]
        return values

    def write_command(self, command):
        """
        Sends the string `command` through the serial connection

        :param str command: the command to send
        """
        if not self.isOpen():
            raise ConnectionClosedError(self)
        self.write(bytearray(command, 'ascii'))

    def measure(self):
        """
        Sends :attr:`~Sensor.read_command` to the sensor, waits
        :attr:`~Sensor.wait_time` milliseconds, and then reads the sensor
        values.
        """
        self.write_command(self.read_command)
        time.sleep(self.wait_time/1000)
        values = self.read_values()
        if len(values) != len(self.measurements):
            raise CorruptDataError(self, ','.join(values))
        return dict(zip(self.measurements, values))
