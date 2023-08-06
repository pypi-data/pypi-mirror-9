__author__ = 'nickmab'

"""A module containing handy custom exceptions used elsewhere in nickmab.async_util"""

class ProducerException(Exception):
    """Exception for wrapping an exception caught in a thread or subproc running a generator

    Attributes:
        caught_exception (Exception): The exception that this ProducerException is wrapping
        message (string): The custom message for this ProducerException which contains the name
            of the generator within which the exception was raised.

    """
    def __init__(self, gen, caught_exception):
        """Init with the generator and the exception that it raised.

        Args:
            gen (generator): The generator in which the wrapped exception was caught.
            caught_exception (Exception): The exception that we caught, which we will store here.

        """
        message = 'Encountered an exception in worker thread of generator \'%s\'' %gen.__name__
        super(Exception, self).__init__(message)
        self.caught_exception = caught_exception

class ConsumerException(Exception):
    """Exception for wrapping an exception caught in a thread or subproc running a coroutine 

    Attributes:
        caught_exception (Exception): The exception that this ConsumerException is wrapping.
        message (string): The custom message for this ProducerException which contains the name
            of the generator within which the exception was raised.

    """
    def __init__(self, coroutine, caught_exception):
        """Init with the coroutine function and the exception that it raised.

        Args:
            gen (generator): The coroutine function in which the wrapped exception was caught.
            caught_exception (Exception): The exception that we caught, which we will store here.

        """
        message = 'Encountered an exception in worker thread of coroutine \'%s\'' %coroutine.__name__
        super(Exception, self).__init__(message)
        self.caught_exception = caught_exception
