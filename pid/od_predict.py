import numpy as np
import os
import tensorflow as tf
import cv2
from collections import defaultdict
from PIL import Image
import pytesseract
from mrz.checker.td3 import TD3CodeChecker
from object_detection.utils import ops as utils_ops
from object_detection.utils import label_map_util
from pid.charger.load_properties import PrepareProperties
from pid.preprocessing.prep import correct_skew
from pid.preprocessing.prep import level_one_preprocessing
from logger.custom_exceptions import InvalidImageFile, ROINotFound, MRZNotValid, TesseractLanguageException
from pid.preprocessing.prep import level_one_preprocessing
import configparser

from logger.logger_helper import Logger
logger = Logger(__name__)


def run_inference_for_single_image(model, image):
    logger.info('Entered run_inference_for_single_image')
    
    image = np.asarray(image)
    input_tensor = tf.convert_to_tensor(image)
    input_tensor = input_tensor[tf.newaxis,...]
    model_fn = model.signatures['serving_default']
    output_dict = model_fn(input_tensor)
    num_detections = int(output_dict.pop('num_detections'))
    output_dict = {key:value[0, :num_detections].numpy() 
                 for key,value in output_dict.items()}
    output_dict['num_detections'] = num_detections
    output_dict['detection_classes'] = output_dict['detection_classes'].astype(np.int64)
    if 'detection_masks' in output_dict:
        detection_masks_reframed = utils_ops.reframe_box_masks_to_image_masks(
                  output_dict['detection_masks'], output_dict['detection_boxes'],
                   image.shape[0], image.shape[1])      
        detection_masks_reframed = tf.cast(detection_masks_reframed > 0.5,
                                           tf.uint8)
        output_dict['detection_masks_reframed'] = detection_masks_reframed.numpy()
    
    logger.info('Exited run_inference_for_single_image')
    return output_dict


def predict(model, image_path):
    """[summary]

    Args:
        model (tf model): model will be loaded and outputs coords, class and confidence score
        image_path (numpy array): path of the image
    """
    logger.info('Entered predict')
    
    config = PrepareProperties()
    PATH_TO_LABELS = config.model_config['labels']['pbtxt']
    category_index = label_map_util.create_category_index_from_labelmap(PATH_TO_LABELS, use_display_name=True)
    try:
        image_np = np.array(Image.open(image_path))
        logger.info('Image read successfully for predict')
    except Exception as e:
        raise InvalidImageFile("Verify the path")


    # image_np = level_one_preprocessing(image_np)
    h, w, _ = image_np.shape
    # Skewness function returns two arguments only rotated image is taken
    # image_np = correct_skew(image_np)


    output_dict = run_inference_for_single_image(model, image_np)
    logger.info('ROI coordinates for single image: obtained successsfully')
    
    boxes = output_dict['detection_boxes']
    max_boxes_to_draw = boxes.shape[0]   #  FORMAT : ymin, xmin, ymax, xmax
    scores = output_dict['detection_scores']   # Desc order highest probability first
#     min_score_thresh=.4
    min_score_thresh=.5
    # min_score_thresh=.3
    coords_label = defaultdict(list)
    # iterating through boxes and appending class, coordinates of BBox and confidence score
    for i in range(min(max_boxes_to_draw, boxes.shape[0])):
        if scores is None or scores[i] > min_score_thresh:
            class_name = category_index[output_dict['detection_classes'][i]]['name']
            coords_label[category_index[output_dict['detection_classes'][i]]['name']].append(scores[i])
            coords_label[category_index[output_dict['detection_classes'][i]]['name']].append(list(boxes[i]))
    
    logger.info('Exited predict')
    return coords_label


def combine_models(model1, model2):
    """Here the output from two models are combined to pick if model looses ROI

    Args:
        model1 (mobile_net_blur): the path of the model
        model2 (efn_blur): the path of the model

    Returns:
        [dict]: the output will be a dictionary with output combined from both models
    """
    logger.info('Entered combine_models')

    combine = {}
    mobile_conf = {}
    efn_conf = {}

    for key, value in model1.items():
        mobile_key = key
        # If many coords are detected for a class get the box with highest confidence
        if len(value) > 2:            
            conf_mobile, coords_mobile = value[0:2]
            mobile_conf[key] = conf_mobile
        else:
            conf_mobile, coords_mobile = value
            mobile_conf[key] = conf_mobile        
        combine[key] = coords_mobile
    
    for key, value in model2.items():
        efn_key = key
        # If many coords are detected for a class get the box with highest confidence
        if len(value) > 2:            
            conf_efn, coords_efn = value[0:2]
            efn_conf[key] = conf_efn
        else:
            conf_efn, coords_efn = value
            efn_conf[key] = conf_efn
        if efn_key not in combine.keys():
            combine[efn_key] = coords_efn
            efn_conf[key] = conf_efn
        # Best working threshold for getting Bbox coords
        elif efn_key in combine.keys() and conf_efn > conf_mobile and mobile_conf[key] < 0.75 and efn_conf[key] > 0.75:
            combine[efn_key] = coords_efn

    # print('mobile conf: ',mobile_conf)
    # print('efn conf: ',efn_conf)
    if len(combine.keys()) == 0:
        raise ROINotFound("ROI not detected")

    logger.info('Exited combine_models')
    return combine

def recognize_character(combine, img_path):
    """
    The function returns the character recognised in the ROI

    Args:
        combine (Dict): It has labels:coords
        img_path (image path)

    Returns:
        [dict]: the output will be a dictionary with keys being ROI labels and value being the recognized character

    """
    logger.info('Entered recognize_character')
    ocr = {}
    img = cv2.imread(img_path, 0)
    logger.info('Image read successfully for recognize_character')
    h, w= img.shape
    for labels ,coords in combine.items():
        if labels == 'mrz_region':
            ymin, xmin, ymax, xmax = coords
            ymin, xmin, ymax, xmax = int(ymin*h), int(xmin*w), int(ymax*h), int(xmax*w)
            cropped_mrz = img[ymin:ymax, xmin:xmax]
            # cropped_mrz = cv2.threshold(cropped_mrz, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
            try:
                tesseract_output = pytesseract.image_to_string(cropped_mrz, lang='mrz')
            except Exception as e:
                raise TesseractLanguageException("Verify MRZ model language is available in the right path")
            logger.debug('Tesseract_output for MRZ region: ' + str(tesseract_output))
            try:
                # tesseract_output = tesseract_output.split('\x0c')[0]
                td3 = TD3CodeChecker(tesseract_output[0:89])
                # td3 = TD3CodeChecker(tesseract_output)
                logger.info('MRZ check done successfully')                
                fields = td3.fields()
                ocr['mrz_surname'] = fields.surname 
                ocr['mrz_name'] = fields.name
                ocr['mrz_country'] = fields.country            
                ocr['mrz_sex'] = fields.sex
                ocr['mrz_birth_date'] = fields.birth_date
                ocr['mrz_expiry_date'] = fields.expiry_date 
                ocr['mrz_document_number'] = fields.document_number
            
            except Exception as e:    # Raise custom exception
                logger.info('MRZ check unsuccessful')
                raise MRZNotValid("MRZ detected is not valid. Check image in the MRZ region")
            
        if labels == 'name':
            ymin, xmin, ymax, xmax = coords
            ymin, xmin, ymax, xmax = int(ymin*h), int(xmin*w), int(ymax*h), int(xmax*w)
            coords_str = [ymin, xmin, ymax, xmax]
            combine[labels] = str(coords_str)
            cropped_name = img[ymin:ymax, xmin:xmax]
            cropped_name = cv2.threshold(cropped_name, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
            try:
                ocr[labels] = pytesseract.image_to_string(cropped_name,lang='name_adcbp')
            except Exception as e:
                raise TesseractLanguageException("Verify Name/surname model language is available in the right path")
            logger.debug('Tesseract_output for name: ' + str(ocr[labels]))

        if labels == 'surname':
            ymin, xmin, ymax, xmax = coords
            ymin, xmin, ymax, xmax = int(ymin*h), int(xmin*w), int(ymax*h), int(xmax*w)
            coords_str = [ymin, xmin, ymax, xmax]
            combine[labels] = str(coords_str)
            cropped_surname= img[ymin:ymax, xmin:xmax]
            cropped_surname = cv2.threshold(cropped_surname, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
            try:
                ocr[labels] = pytesseract.image_to_string(cropped_surname,lang='name_adcbp')
            except Exception as e:
                raise TesseractLanguageException("Verify Name/surname model language is available in the right path")

            logger.debug('Tesseract_output for surname: ' + str(ocr[labels]))

    logger.info('Exited recognize_character')
    return ocr
