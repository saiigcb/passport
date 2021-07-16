from scipy.ndimage import interpolation as inter
import random
import cv2
import numpy as np
from logger.logger_helper import Logger
from PIL import Image, ImageStat, ImageEnhance
from pid.charger.load_properties import PrepareProperties

logger = Logger(__name__)
charge = PrepareProperties()

def get_brightness(image):
    grey = image.convert('L')
    stat = ImageStat.Stat(grey)
    logger.info("Brightness value: "+str(stat.mean[0]))
    return stat.mean[0]

def get_contrast(image):
    grey = image.convert('L')
    stat = ImageStat.Stat(grey)
    logger.info("contrast value: "+str(stat.stddev[0]))  
    return stat.stddev[0]

def adjust_brightness(image, brightness, card_name = 'passport_preprocessing'):
    enhance_factor_l = charge.model_config.getfloat(card_name, 'enhance_factor_l')   # comes from card_type.ini but how it's coming
    enhance_factor_u = charge.model_config.getfloat(card_name, 'enhance_factor_u')   # because it's in public so cards_config accessible
    brightness_level_u = charge.model_config.getint(card_name, 'brightness_level_u')
    enhance_factor = enhance_factor_l
    if brightness >= brightness_level_u:
        enhance_factor = enhance_factor_u
    enhance_bri = ImageEnhance.Brightness(image)
    return enhance_bri.enhance(enhance_factor)

def adjust_contrast(image, contrast, card_name = 'passport_preprocessing'):
    enhance_factor_l = charge.model_config.getfloat(card_name, 'enhance_factor_l')
    contrast_level_u = charge.model_config.getint(card_name, 'contrast_level_u')
    enhance_factor_u = charge.model_config.getfloat(card_name, 'enhance_factor_u')
    enhance_factor = enhance_factor_l
    if contrast >= contrast_level_u:
        enhance_factor = enhance_factor_u
    enhance_cont = ImageEnhance.Contrast(image)
    return enhance_cont.enhance(enhance_factor)


# check brightness and contrast level and adjust brightness and constrast
def check_level(image, card_name = 'passport_preprocessing'):
    logger.info("level one pre processing started")
    brightness = get_brightness(image)
    contrast = get_contrast(image)
    brightness_level_l = charge.model_config.getint(card_name, 'brightness_level_l')
    brightness_level_u = charge.model_config.getint(card_name, 'brightness_level_u')
    contrast_level_l = charge.model_config.getint(card_name, 'contrast_level_l')
    contrast_level_u = charge.model_config.getint(card_name, 'contrast_level_u')
    if int(brightness) not in range(brightness_level_l, brightness_level_u):
        image = adjust_brightness(image, brightness, card_name)
        image = check_level(image, card_name)
        # return image
    elif int(contrast) not in range(contrast_level_l, contrast_level_u):
        image = adjust_contrast(image, contrast, card_name)
        image = check_level(image, card_name)
        # return image
    
    return image


def level_one_preprocessing(opencv_image, card_name = 'passport_preprocessing'):
    # convert opencv image to PIL image
    image = Image.fromarray(cv2.cvtColor(opencv_image, cv2.COLOR_BGR2RGB))
    image = check_level(image, card_name)
    logger.info("Image conversion completed")
    return np.array(image), get_brightness(image), get_contrast(image)

def determine_score(arr, ang):
    data = inter.rotate(arr, ang, reshape=False, order=0)  # rotate image(arr) with angle
    hist = np.sum(data, axis=1)  # sum the array - axis=1 -row wise (histogram)
    scr= np.sum((hist[1:] - hist[:-1]) ** 2)  # calculate the score by sum and square
    return hist, scr  # returning histogram and score

def correct_skew(image, delta=.1, limit=20):
    gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)  # convert image tp grayscale
    blur = cv2.medianBlur(gray, 3)  # applying blur to image
    thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]  # convert greyscale to binary

    scores = []  # assign a empty array
    angles = np.arange(-limit, limit + delta, delta)  # make an array of angles
    for angle in angles:
        histogram, score = determine_score(thresh, angle)
        scores.append(score)

    best_angle = angles[scores.index(max(scores))]   # finding the best angle

    (h, w) = image.shape[:2]
    center = (w // 2, h // 2)
    m = cv2.getRotationMatrix2D(center, best_angle, 1.0)
    rotated = cv2.warpAffine(image, m, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
    rotated_image = cv2.cvtColor(rotated, cv2.COLOR_BGR2RGB)
    return rotated_image

