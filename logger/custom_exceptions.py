""" SoB Custom Exceptions"""
from pid.charger.load_properties import PrepareProperties
from logger.logger_helper import Logger

logger = Logger(__name__)
#Read error codes property files
charged_properties = PrepareProperties()
error_codes = charged_properties.system_config['error_codes']

class ADCBError(Exception):

    def __init__(self, message=None, errorno=-1):
        super().__init__(message)
        self.message = message
        self.errorno = errorno
        #self.log_msg = '{} - {} '.format(self.errorno, self.message)
    def __str__(self):
        if self.message:
            return self.message
        return "-1"

class MalformedRequestBody(ADCBError):
    def __init__(self, message):
        msg = "Malformed Request Body Error: " + message
        super().__init__(msg, errorno =  error_codes[type(self).__name__])

class InvalidImageFile(ADCBError):
    def __init__(self, message):
        msg = "Invalid Image File: " + message
        super().__init__(msg, errorno =  error_codes[type(self).__name__])


# class InvalidRequestMethod(ADCBError):
#     """
#     This is used when REST is not used
#     GET / POST METHODS check
#     Req: POST

#     Args:
#         ADCBError ([type]): [description]
#     """
#     def __init__(self, message):
#         msg = "Invalid Request Method: " +  message
#         super().__init__(msg, errorno =  error_codes[type(self).__name__])

class DBConnectionError(ADCBError):
    def __init__(self, message):
        msg = "DB Connection Error: " + message
        super().__init__(msg, errorno =  error_codes[type(self).__name__])


class TesseractLanguageException(ADCBError):
    def __init__(self, message):
        msg = "Tesseract Language Exception: " +  message
        super().__init__(msg, errorno =  error_codes[type(self).__name__])


class ROINotFound(ADCBError):
    def __init__(self, message):
        msg = "ROI for OCR Data Not Found: " +  message
        super().__init__(msg, errorno =  error_codes[type(self).__name__])
    
class MRZNotValid(ADCBError):
    def __init__(self, message):
        msg = "MRZ is Not valid: " +  message
        super().__init__(msg, errorno =  error_codes[type(self).__name__])


