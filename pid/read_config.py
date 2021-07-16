from configparser import ConfigParser

def read_config():
    file = './config_files/predict.ini'
    config = ConfigParser(allow_no_value=True)
    config.read(file)
    return config