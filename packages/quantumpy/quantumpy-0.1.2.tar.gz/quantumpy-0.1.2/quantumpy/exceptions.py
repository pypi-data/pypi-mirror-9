class QuantumPythonError(Exception):
    """ Base exception """

class QuantumError(QuantumPythonError):
    """ Exception for the Quantum API errors """

class AuthenticationError(QuantumError):
    """ Exception for the Quantum API authentication errors """

class HandlerNotFoundError(QuantumError):
    """ Exception for the Quantum API endpoint errors """

class InternalServerError(QuantumError):
    """ Exception for Quantum API's internal serer errors """

class HTTPError(QuantumPythonError):
    """ Exception for http errors """
