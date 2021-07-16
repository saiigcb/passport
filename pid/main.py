import numpy as np
import os
import six.moves.urllib as urllib
import sys
import tensorflow as tf
import cv2
from collections import defaultdict
from io import StringIO
from PIL import Image
from django.http import JsonResponse
from rest_framework.decorators import api_view
from pid.od_predict import predict, combine_models, recognize_character
from object_detection.utils import ops as utils_ops
from object_detection.utils import label_map_util
from pid.charger.load_model import PrepareModel
from pid.charger.load_properties import PrepareProperties
from logger.logger_helper import Logger
from logger.custom_exceptions import MalformedRequestBody
from logger.exception_handler import form_error_resp
import uuid
import traceback
import json

logger = Logger(__name__)
#Read error codes property files
charged_properties = PrepareProperties()


# Create your views here.
@api_view(('POST',))
def request_handler(request):
    try:
        logger.info('Entered request_handler')
        audit_id = str(uuid.uuid4())
        request.user.__setattr__("audit_id", audit_id)   # every hit random number assigned to user
        models = PrepareModel()
        logger.info('Model loaded successfully')
        req_data = request.body
        req_json = req_data.decode('utf8')
        logger.info('Request Received successfully')
        
        data = json.loads(req_json)
        keys_list = ['img_path','reference_number']   # verify whether required parameters are there
        if not data or not set(keys_list).issubset(set(data.keys())):
            raise MalformedRequestBody("One or more keys are missed in request body")
        img = data['img_path']
        ref_number = data['reference_number']

        logger.debug('Request data: ' + str(data))
        
        mobile = models.mobile
        efn = models.efn
        
        out_mobile = predict(mobile, img)
        logger.debug('Model1 prediction: ' + str(out_mobile))
        out_efn = predict(efn, img)
        logger.debug('Model2 prediction: ' + str(out_efn))
        
        combine = combine_models(out_mobile, out_efn)
        logger.debug('Model1 and model2 prediction combined: ' + str(combine))
        final_output = recognize_character(combine, img)
        logger.debug('OCR done: ' + str(final_output))

        final_output['ref_number'] = ref_number
        final_output['error_no'] = '000'
        final_output['error_description'] = charged_properties.system_config['res_error_desc']['000']
        logger.debug('Final output: ' + str(final_output))

        logger.info('Exited request_handler')
        return JsonResponse(final_output)
    except Exception as e:
        output = form_error_resp(e, traceback.format_exc())
        return JsonResponse(output)
