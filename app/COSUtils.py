import ibm_boto3
from ibm_botocore.client import Config
from botocore.exceptions import ClientError
import pandas as pd
import logging
from app.constants import Constants
class COSUtils():
    def __init__(self):
        """
        Description : Constructor to class COSUtils, initializes the connection to COS

        Parameters : 1. self

        """
        constants = Constants()
        self.client = ibm_boto3.client(service_name='s3',ibm_api_key_id=constants.API_KEY,ibm_auth_endpoint=constants.AUTH_ENDPOINT,config=Config(signature_version='oauth'),endpoint_url=constants.COS_API_ENDPOINT)

    def get_dataframe(self, column_names, bucket, filename):
        """
        Description : To get a file from a cos bucket and store in pandas dataframe.  

        Parameters : 1. self
                     2. column_names - column names of the pandas data frame
                     3. bucket - COS bucket containing the file
                     4. filename - Name of the file to be fetched

        Return Value : Pandas dataframe containing the file contents
        """
        logging.info("Fetching "+filename+" from cos bucket "+bucket)
        # Setting up a connection to COS to get a file from a bucket
        try:
            body = self.client.get_object(Bucket=bucket,Key=filename)['Body']
            if not hasattr(body, "__iter__"): body.__iter__ = types.MethodType( __iter__, body )
            logging.debug("File Read from COS")
            df = pd.read_csv(body, header = None, skiprows=[0], names = column_names)
            df.columns = column_names
            logging.debug("File stored in Pandas")
            return df
        except ClientError as be:
            logging.error("CLIENT ERROR: {0}\n".format(be))
        except (NameError, FileNotFoundError) as e:
            logging.error("Error: File Not Found \n {0}".format(e))
        except Exception as e:
            logging.error("Error retrieving/reading file \n {0}".format(e))
        


    def write_dataframe(self, df, column_names, bucket, filename):
        """
        Description : To write a pandas dataframe to COS 

        Parameters : 1. self
                     2. df - the pandas dataframe to be written to COS
                     3. column_names - column names of the pandas data frame
                     4. bucket - COS bucket to upload the file
                     5. filename - Name of the file to be stored

        Return Value : Pandas dataframe containing the file contents
        """
        logging.info("Writing file to cos bucket "+bucket)
        df.columns = column_names
        try:
            # Storing the file in a Pandas Dataframe
            df.to_csv(filename, index=False)
            # Uploading the file to COS
            self.client.upload_file(Filename=filename,Bucket=bucket,Key=filename)
            logging.debug("File stored in COS")
        except ClientError as be:
            logging.error("CLIENT ERROR: {0}\n".format(be))
        except Exception as e:
            logging.error("Unable to retrieve file from COS Bucket: {0}".format(e))