import os, sys
import pandas as pd
import json

from housing.logger import logging
from housing.exception import HousingException
from housing.entity.artifact_entity import DataIngestionArtifact,DataValidationArtifact
from housing.entity.config_entity import DataValidationConfig
from housing.util.util import read_yaml_file
from housing.constant import *

from evidently.report import Report

class DataValidation:
    def __init__(self, data_ingestion_artifact: DataIngestionArtifact,data_validation_config:DataValidationConfig):
        try:
            logging.info(f"{'>>'*30}Data Valdaition log started.{'<<'*30} \n\n")
            self.data_ingestion_artifact=data_ingestion_artifact
            self.data_validation_config=data_validation_config
        except Exception as e:
            raise HousingException(e,sys) from e
        

    def get_train_and_test(self):
        try:
            train_df=pd.read_csv(self.data_ingestion_artifact.train_file_path)
            test_df=pd.read_csv(self.data_ingestion_artifact.test_file_path)
            return train_df,test_df
        except Exception as e:
            raise HousingException(e,sys) from e
        

    def is_train_test_file_exists(self):
        try:
            logging.info('Checking if train and test file exists')

            does_train_file_exist=False
            does_test_file_exist=False

            train_file_path=self.data_ingestion_artifact.train_file_path
            test_file_path=self.data_ingestion_artifact.test_file_path

            does_train_file_exist=os.path.exists(train_file_path)
            does_test_file_exist=os.path.exists(test_file_path)

            is_available=does_train_file_exist and does_test_file_exist

            logging.info(f'Does train and test file exist? {is_available}')

            if not is_available:
                train_file=self.data_ingestion_artifact.train_file_path
                test_file=self.data_ingestion_artifact.test_file_path
                message=f"Train file: [{train_file}] and Test file: [{test_file}] does not exist"
                logging.info(f"{message}")
                raise Exception(message)
            return is_available
        except Exception as e:
            raise HousingException(e,sys) from e
        

    def validate_dataset_schema(self,input):
        try:
            schema_file_path=os.path.join(ROOT_DIR,CONFIG_DIR,SCHEMA_FILE)
            schema=read_yaml_file(schema_file_path)
            incoming_data=dict(zip(schema['numerical_columns']+schema['categorical_columns'],input))
            domain_values=schema['domain_value']['ocean_proximity']
            numerical_columns= schema['numerical_columns']
            categorical_columns= schema['categorical_columns']
            
            validation_status=True
            #1. Check number of columns
            if len(input) != 9:
                validation_status=False

            #2. Checking values of ocean proximity
            if incoming_data['ocean_proximity'] not in domain_values:
                validation_status=False

            #3. Check for datatype
            for key,value in incoming_data.items():
                if key in categorical_columns:
                    if not isinstance(value,str):
                        validation_status=False
                elif key in numerical_columns:
                    if not isinstance(value,int) and not isinstance(value,float):
                        validation_status=False
            logging.info(f"Is the data valid? [{validation_status}]")
            return validation_status
        except Exception as e:
            raise HousingException(e,sys) from e
        
    
    def get_and_save_data_drift_report(self):
        try:
            logging.info('Creating a report to check for Data drift')
            profile=Profile(sections=[DataDriftProfileSection()])

            train,test=self.get_train_and_test()

            profile.calculate(train,test)
            report=json.loads(profile.json())

            report_file_path=self.data_validation_config.report_file_path
            report_dir=os.path.dirname(report_file_path)
            os.makedirs(report_dir,exist_ok=True)

            with open(report_file_path,'w') as report_file:
                logging.info('Dumping the report to: [{report_file_path}]')
                json.dump(report,report_file,indent=6)
            return report
        except Exception as e:
            raise HousingException(e,sys) from e
        
    
    def save_data_drift_report_page(self):
        try:
            dashboard=Dashboard(tabs=(DataDriftTab()))
            train,test=self.get_train_and_test()
            dashboard.calculate(train,test)

            report_page_file_path=self.data_validation_config.report_page_file_path
            report_dir=os.path.dirname(report_page_file_path)
            os.makedirs(report_dir,exist_ok=True)

            dashboard.save(report_page_file_path)
        except Exception as e:
            raise HousingException(e,sys) from e
        
    
    def is_data_drift_found(self):
        try:
            report=self.get_and_save_data_drift_report()
            self.save_data_drift_report_page()
            return True
        except Exception as e:
            raise HousingException(e,sys) from e
        

    def initiate_data_validation(self)->DataValidationArtifact :
        try:
            _,test=self.get_train_and_test()
            self.is_train_test_file_exists()
            #self.is_data_drift_found()
            self.validate_dataset_schema(input=test)

            data_validation_artifact = DataValidationArtifact(
                schema_file_path=self.data_validation_config.schema_file_path,
                report_file_path=self.data_validation_config.report_file_path,
                report_page_file_path=self.data_validation_config.report_page_file_path,
                is_validated=True,
                message="Data Validation performed successully."
            )
            logging.info(f"Data validation artifact: {data_validation_artifact}")
            return data_validation_artifact
        except Exception as e:
            raise HousingException(e,sys) from e
        

    
    def __del__(self):
        logging.info(f"{'>>'*30}Data Valdaition log completed.{'<<'*30} \n\n")