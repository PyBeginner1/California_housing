import sys

from housing.config.configuration import Configuration
from housing.entity.artifact_entity import DataIngestionArtifact
from housing.entity.config_entity import DataIngestionConfig
from housing.logger import logging
from housing.exception import HousingException
from housing.component.data_ingestion import DataIngestion


class Pipeline:
    def __init__(self, config: Configuration):
        try:
            self.config=config
        except Exception as e:
            raise HousingException(e,sys) from e
        
    
    def start_data_ingestion(self)->DataIngestionArtifact:
        try:
            data_ingestion=DataIngestion(data_ingestion_config=self.config.get_data_ingestion_config())
            return data_ingestion.initiate_data_ingestion()
        except Exception as e:
            raise HousingException(e,sys) from e
        

    def start_data_validation(self):
        try:
            pass
        except Exception as e:
            raise HousingException(e,sys) from e
        

    def start_data_transformation(self):
        try:
            pass
        except Exception as e:
            raise HousingException(e,sys) from e
        
    
    def start_model_trainer(self):
        try:
            pass
        except Exception as e:
            raise HousingException(e,sys) from e
        
    
    def start_model_evaluation(self):
        try:
            pass
        except Exception as e:
            raise HousingException(e,sys) from e
        

    def start_model_pusher(self):
        try:
            pass
        except Exception as e:
            raise HousingException(e,sys) from e
        
        
    #Run all the above components
    def run_pipeline(self):
        try:
            data_ingestion_artifact=self.start_data_ingestion()
        except Exception as e:
            raise HousingException(e,sys) from e