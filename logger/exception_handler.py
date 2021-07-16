from logger.custom_exceptions import ADCBError, MalformedRequestBody, DBConnectionError
from logger.logger_helper import Logger
# from pid.utils import get_request_parameters
# from audit.audit_handler import AuditHandler
from pid.charger.load_properties import PrepareProperties
charged_properties = PrepareProperties()

logger = Logger(__name__)


def form_error_resp(exception, tb_msg):
    output = dict()
    logger.error(str(exception) + '\n' + tb_msg)
    error_no = 999    # unknown error default
    if isinstance(exception, ADCBError):
        error_no = exception.errorno
        err_msg = charged_properties.system_config['res_error_desc'][str(error_no)]
    else:
        err_msg = charged_properties.system_config['res_error_desc'][str(error_no)]

    # This is only for audit
    # if not isinstance(exception,DBConnectionError):
    #     if isinstance(exception,MalformedRequestBody):
    #         audit = AuditHandler(' ', -1, ' ', ' ', ' ', ' ', 
    #                             'Exception', 'Failed', str(exception) + ' ' +tb_msg , ' ')
    #         audit.log_audit_data()
    #     else:
    #         req_data = get_request_parameters()
    #         audit = AuditHandler(req_data['audit_id'], -1,req_data['channel_name'], req_data['filename'], req_data['app_version'], req_data['client_os'],
    #                                 'Exception', 'Failed',  str(exception) + ' ' +tb_msg , req_data['reference_number'] )
    #         audit.log_audit_data()
    output['error_no'] = error_no
    output['error_description'] = err_msg
    logger.debug("final output: " + str(output))
    return output
