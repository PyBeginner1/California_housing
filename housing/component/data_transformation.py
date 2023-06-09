import os, sys
import pandas as pd
import numpy as np

from housing.logger import logging
from housing.exception import HousingException
from housing.entity.config_entity import DataTransformationConfig
from housing.entity.artifact_entity import DataIngestionArtifact,DataValidationArtifact,DataTransformationArtifact
from housing.util.util import read_yaml_file,load_data,save_numpy_array_data,save_object
from housing.constant import *

from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler,OneHotEncoder
from sklearn.impute import SimpleImputer


class DataTransformation:
    def __init__(self,data_transformation_config:DataTransformationConfig,
                        data_ingestion_artifact:DataIngestionArtifact,
                        data_validation_artifact:DataValidationArtifact):
        try:
            self.data_transformation_config=data_transformation_config
            self.data_ingestion_artifact=data_ingestion_artifact
            self.data_validation_artifact=data_validation_artifact
        except Exception as e:
            logging.info(f"{e}")
            raise HousingException(e,sys) from e 
    

    def get_data_transformer_object(self)->ColumnTransformer:
        try:
            schema_file_path=self.data_validation_artifact.schema_file_path

            dataset_schema=read_yaml_file(schema_file_path)

            numerical_cols=dataset_schema[NUMERICAL_COLUMN_KEY]
            categorical_cols=dataset_schema[CATEGORICAL_COLUMN_KEY]

            num_pipeline=Pipeline(steps=[
                ('impute',SimpleImputer(strategy='median')),
                ('scaler',StandardScaler())
            ])

            cat_pipeline=Pipeline(steps=[
                ('impute',SimpleImputer(strategy='most_frequent')),
                ('one_hot_encoder',OneHotEncoder()),
                ('scaler',StandardScaler(with_mean=False))
            ])

            logging.info(f"Numerical columns: {numerical_cols}")
            logging.info(f"Categorical columns: {categorical_cols}")

            preprocessing=ColumnTransformer(
                [
                ('num_pipeline',num_pipeline,numerical_cols),
                ('cat_pipeline',cat_pipeline,categorical_cols)
                ]
            )
            
            return preprocessing
        except Exception as e:
            raise HousingException(e,sys) from e



    def initiate_data_transformation(self):
        try:
            logging.info(f"Obtaining preprocessing object.")
            preprocessing_obj = self.get_data_transformer_object()


            logging.info(f"Obtaining training and test file path.")
            train_file_path = self.data_ingestion_artifact.train_file_path
            test_file_path = self.data_ingestion_artifact.test_file_path
            

            schema_file_path = self.data_validation_artifact.schema_file_path
            
            logging.info(f"Loading training and test data as pandas dataframe.")
            train_df = load_data(file_path=train_file_path, schema_file_path=schema_file_path)
            
            test_df = load_data(file_path=test_file_path, schema_file_path=schema_file_path)

            schema = read_yaml_file(file_path=schema_file_path)

            target_column_name = schema[TARGET_COLUMN_KEY]


            logging.info(f"Splitting input and target feature from training and testing dataframe.")
            input_feature_train_df = train_df.drop(columns=[target_column_name],axis=1)
            target_feature_train_df = train_df[target_column_name]

            input_feature_test_df = test_df.drop(columns=[target_column_name],axis=1)
            target_feature_test_df = test_df[target_column_name]
            

            logging.info(f"Applying preprocessing object on training dataframe and testing dataframe")
            input_feature_train_arr=preprocessing_obj.fit_transform(input_feature_train_df)
            input_feature_test_arr = preprocessing_obj.transform(input_feature_test_df)


            train_arr = np.c_[ input_feature_train_arr, np.array(target_feature_train_df)]
            test_arr = np.c_[input_feature_test_arr, np.array(target_feature_test_df)]

            final_train_df=pd.DataFrame(train_arr)
            final_test_df=pd.DataFrame(test_arr)
            
            transformed_train_dir = self.data_transformation_config.transformed_train_dir
            transformed_test_dir = self.data_transformation_config.transformed_test_dir

            train_file_name = os.path.basename(train_file_path)
            test_file_name = os.path.basename(test_file_path)

            transformed_train_file_path = os.path.join(transformed_train_dir, train_file_name)
            transformed_test_file_path = os.path.join(transformed_test_dir, test_file_name)

            logging.info(f"Saving transformed training and testing array.")

            os.makedirs(os.path.dirname(transformed_train_file_path),exist_ok=True)
            os.makedirs(os.path.dirname(transformed_test_file_path),exist_ok=True)

            final_train_df.to_csv(transformed_train_file_path,index=False)
            final_test_df.to_csv(transformed_test_file_path,index=False)
        

            preprocessing_obj_file_path = self.data_transformation_config.preprocessed_object_file_path

            logging.info(f"Saving preprocessing object.")
            save_object(file_path=preprocessing_obj_file_path,obj=preprocessing_obj)

            data_transformation_artifact = DataTransformationArtifact(is_transformed=True,
            message="Data transformation successfull.",
            transformed_train_file_path=transformed_train_file_path,
            transformed_test_file_path=transformed_test_file_path,
            preprocessed_object_file_path=preprocessing_obj_file_path

            )
            logging.info(f"Data transformation artifact: {data_transformation_artifact}")
            return data_transformation_artifact
        except Exception as e:
            raise HousingException(e,sys) from e
        

    def __del__(self):
        logging.info(f"{'>>'*30}Data Transformation log completed.{'<<'*30} \n\n")
    