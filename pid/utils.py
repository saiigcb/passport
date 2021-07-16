import json
import os
from django_middleware_global_request.middleware import get_request

def get_request_parameters():
    req_data=dict()
    request = get_request()
    req_data['audit_id'] = request.user.audit_id 
    data = json.loads(request.body)
    image_path = data['image_path']
    req_data['filename'] = os.path.basename(image_path)
    req_data['reference_number'] = data['reference_number']
    req_data['channel_name'] = data['channel_name']
    req_data['app_version'] = data['app_version']
    req_data['client_os'] = data['client_os']
    return req_data