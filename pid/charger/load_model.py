"""This module loads all the model in cards.ini file"""
from pid.charger.load_properties import PrepareProperties
import tensorflow as tf
class PrepareModel:
    """Singleton class to manage concurrent thread generation"""

    class __impl:
        def __init__(self):
            config = PrepareProperties()
            self.model_name1 = config.model_config['model_path']['model1']
            self.mobile = tf.saved_model.load(self.model_name1)
            self.model_name2 = config.model_config['model_path']['model2']
            self.efn = tf.saved_model.load(self.model_name2)

    instance = None

    def __new__(cls):
        if not PrepareModel.instance:
            PrepareModel.instance = PrepareModel.__impl()
        return PrepareModel.instance

    def __getattr__(self, name):
        return getattr(self.instance, name)

    def __setattr__(self, name, value):
        return setattr(self.instance, name, value)

