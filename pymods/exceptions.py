""" This module contains custom exceptions specific to the SWOT reprojection
    tool. These exceptions are intended to allow for easier debugging of the
    expected errors that may occur during an invocation of the service.

"""

class CustomError(Exception):
    """ Base class for exceptions in the SWOT reprojection tool. This base
        class could be extended in the future to assign exit codes, for
        example.

    """
    def __init__(self, exception_type, message):
        self.exception_type = exception_type
        self.message = message
        super().__init__(self.message)


class MissingReprojectedDataError(CustomError):
    """ This exception is raised when an expected single-band output file
        containing reprojected data for a science variable is not found by
        the `create_output` function in `nc_merge.py`.

    """
    def __init__(self, missing_variable):
        super().__init__('MissingReprojectedDataError',
                         ('Could not find reprojected output file for '
                          f'{missing_variable}.'))