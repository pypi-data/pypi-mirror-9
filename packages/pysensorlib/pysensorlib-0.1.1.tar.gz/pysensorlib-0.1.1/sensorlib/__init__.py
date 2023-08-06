__version__ = '0.1.1'
__all__ = ['Sensor', 'SensorError']


class SensorError(Exception):
    """
    Base error class for all errors in this module

    :param sensor: the :class:`~sensorlib.Sensor` for which this exception
        occurred
    """
    def __init__(self, sensor):
        self.sensor = sensor


class Sensor(object):
    """
    Abstract interface that represents a single sensor. Any classes that read
    from sensors should inherit from this class.

    :param list measurements: a list of the names of the measurements that this
        sensor takes
    """
    def __init__(self, measurements):
        self.measurements = measurements

    def measure(self):
        """
        Measures whatever parameters this sensor can measure. Subclasses of
        :class:`~sensorlib.Sensor` must implement this function.

        :return: a dictionary that maps measurement names to read values
        """
        raise NotImplementedError("Subclasses of Sensor must implement measure")
