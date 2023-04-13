import os,sys
import yaml


from housing.exception import HousingException
from housing.logger import logging




def read_yaml_file(file_path:str)->dict:
    """
    Reads yaml file and returns dictionary
    """
    try:
        with open(file_path,'r') as yaml_file:
            logging.info('Reading Yaml file')
            return yaml.safe_load(yaml_file)
    except Exception as e:
        logging.info(e)
        raise HousingException(e,sys) from e