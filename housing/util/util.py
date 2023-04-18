import os,sys
import yaml
import pandas as pd
import numpy as np
import dill

from housing.exception import HousingException
from housing.logger import logging
from housing.constant import *



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
    


def load_data(file_path:str,schema_file_path:str)->pd.DataFrame:
    try:
        dataset_schema=read_yaml_file(schema_file_path)
        schema=dataset_schema[DATASET_SCHEMA_COLUMNS_KEY]

        data=pd.read_csv(file_path)

        error_message=""

        for col in data.columns:
            if col in list(schema.keys()):
                data[col].astype(schema[col])
            else:
                error_message = f"{error_message} \nColumn: [{col}] is not in the schema."

        if len(error_message)>0:
            raise Exception(error_message)
        return data
    except Exception as e:
        logging.info(e)
        raise HousingException(e,sys) from e
    

###Delete 
def save_numpy_array_data(file_path:str,array:np.array):
    try:
        dir_path = os.path.dirname(file_path)
        os.makedirs(dir_path, exist_ok=True)
        with open(file_path, 'wb') as file_obj:
            np.save(file_obj, array)
    except Exception as e:
        raise HousingException(e, sys) from e



def save_object(file_path:str,obj):
    try:
        dir_path=os.path.dirname(file_path)
        os.makedirs(dir_path,exist_ok=True)
        with open(file_path,"wb") as file_obj:
            dill.dump(obj,file_obj)
    except Exception as e:
        logging.info(e)
        raise HousingException(e,sys) from e
