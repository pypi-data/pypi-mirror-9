"""Client exceptions."""

class OkException(BaseException):
    """Base exception for ok.py."""
    pass

class UsageException(BaseException):
    """Usage exception for errors in using ok.py"""

# TODO(albert): extend from a base class designed for student bugs.
class Timeout(UsageException):
    """Exception for timeouts."""
    _message = 'Evaluation timed out!'

    def __init__(self, timeout):
        """Constructor.

        PARAMTERS:
        timeout -- int; number of seconds before timeout error occurred
        """
        super().__init__(self)
        self.timeout = timeout
        self.message = _message

class FileNotFoundException(UsageException):
    """Exception for files not being found."""
    
    def __init__(self, filename):
        """Constructor.

        PARAMETERS:
        filename -- str; the file that couldn't be found
        """
        self._filename = filename

    @property
    def message(self):
        return "Required file not found: {}".format(self._filename)

class LargeEditDistanceError(UsageException):
    """Exception for really large edit distances."""

    def __init__(self, question, tests):
        """Constructor

        PARAMETERS:
        question -- str; the input that was given
        tests -- array; an array of tests to be matched
        """
        self.message = 'Unable to correct mistyped question: {}\n'.format(question)
        self.message += 'Here are the questions with tests:\n'
        for test in tests:
            self.message += '    {}\n'.format(test)

class DeserializeError(OkException):
    """Exceptions related to deserialization."""

    @classmethod
    def expect_dict(cls, json):
        return cls('Expected JSON dict, got {}'.format(
            type(json).__name__))

    @classmethod
    def expect_list(cls, json):
        return cls('Expected JSON list, got {}'.format(
            type(json).__name__))

    @classmethod
    def missing_fields(cls, fields):
        return cls('Missing fields: {}'.format(
            ', '.join(fields)))

    @classmethod
    def unexpected_field(cls, field):
        return cls('Unexpected field: {}'.format(field))

    @classmethod
    def unexpected_value(cls, field, expect, actual):
        return cls(
            'Field "{}" expected value {}, got {}'.format(
                field, expect, actual))

    @classmethod
    def unexpected_type(cls, field, expect, actual):
        return cls(
            'Field "{}" expected type {}, got {}'.format(
                field, expect, repr(actual)))

    @classmethod
    def unknown_type(cls, type_, case_map):
        return cls(
            'TestCase type "{}" is unknown in case map {}'.format(
                type_, case_map))

