"""Used to store errors and print a error report
"""
import sys

class ErrorReport(object):
    """Used for keeping track of errors and reporting errors
    """

    def __init__(self):
        self.error_report = {}


    def add_error(self, error_str, line_number):
        """For an error type, add to report"""
        print('\033[93m'
              + error_str
              + " on line number "
              + str(line_number)
              + '\033[0m')

        if error_str in self.error_report:
            self.error_report[error_str]['count'] = self.error_report[error_str]['count'] + 1
            self.error_report[error_str]['lines'].append(str(line_number))
        else:
            error_detail = {}
            error_detail['count'] = 1
            error_detail['lines'] = [str(line_number)]
            self.error_report[error_str] = error_detail


    def get_errors(self):
        """ Prints out error report to console """
        if self.error_report:
            return self.error_report
        else:
            return False
