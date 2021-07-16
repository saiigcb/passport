"""this module loads all the properties variables required"""
import os
import configparser

class PrepareProperties:
    """Singleton class to manage concurrent thread generation"""
    class __impl:
        """
        Making the PrepareProperties class a singleton class so that
        the Properties will not be loaded multiple times this class will load the Properties
        and make it accessible globaly
        """
        def __init__(self):
            BASEDIR = os.path.dirname(os.path.realpath(__file__))
            BASEDIR = os.path.split(BASEDIR)[0]
            BASEDIR = os.path.join(BASEDIR, 'config_files')
            MODEL_BASEDIR = os.path.join(BASEDIR, 'predict.ini')
            self.model_config = configparser.ConfigParser()
            self.model_config.read(MODEL_BASEDIR)
            # DB, Error codes, ASync mode
            SYSTEM_BASEDIR = os.path.join(BASEDIR, 'sysconfig.ini')
            self.system_config = configparser.ConfigParser()
            self.system_config.read(SYSTEM_BASEDIR)


    instance = None
    def __new__(cls):
        if not PrepareProperties.instance:
            PrepareProperties.instance = PrepareProperties.__impl()
        return PrepareProperties.instance

    def __getattr__(self, name):
        return getattr(self.instance, name)

    def __setattr__(self, name, value):
        return setattr(self.instance, name, value)
