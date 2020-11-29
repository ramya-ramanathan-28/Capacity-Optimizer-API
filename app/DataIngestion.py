from app.COSUtils import COSUtils
import datetime
import requests
from app.constants import Constants
from abc import ABCMeta, abstractmethod
import logging
import configparser
import json
import csv
import pandas as pd
class DataIngestion():
    """
    Description: Abstract class for Data Ingestion
    """
    @abstractmethod
    def setQuery(self, start, end, clusterName):
        """
        Description : Creates the query to access to New Relic Endpoint

        Parameters : 1. self
                     2. start - timestamp from which data should be fetched
                     3. end - timestamp upto which data should be fetched
                     4. clusterName - cluster from which data is to be fetched

        Return Value : Query used to get the required data
        """
        pass
    @abstractmethod
    def sendRequest(self, query):
        """
        Description : Accesses the new relic query end point and fetches the data

        Parameters : 1. self
                     2. query - to query the new relic data

        Return Value : Response of the New Relic Query
        """

        pass
    @abstractmethod
    def createDataset(self, Region, days='1')):
        """
        Description : Converting the API response to a dataset

        Parameters : 1. self
                     2. region - the region where instances are to be predicted
                     3. days - number of days of data to be fetched

        Return Value : Pandas dataframe containing the new relic response
        """
        pass



class NewRelicDataIngestion(DataIngestion):
    def setQuery(self, start, end, clusterName):
        """
        Description : Creates the query to access to New Relic Endpoint

        Parameters : 1. self
                     2. start - timestamp from which data should be fetched
                     3. end - timestamp upto which data should be fetched
                     4. clusterName - cluster from which data is to be fetched

        Return Value : Query used to get the required data
        """
        logging.debug("Creating New Relic Query")
       
        
        nrql='''SELECT cpuRequestPerPod,instances from dataplane_capacity where clusterID=\''''+clusterName+'''\' since \'''' + start + '''\' until \'''' + end +  '''\' limit 1000 order by timestamp'''
        logging.debug(nrql)
        return nrql


    def sendRequest(self, query):
        """
        Description : Accesses the new relic query end point and fetches the data

        Parameters : 1. self
                     2. query - to query the new relic data

        Return Value : Response of the New Relic Query
        """
        logging.debug("Getting daily data from New Relic API")
        

        #Accessing NewRelic API with Query
        try:
            
            data = {"nrql":query} 
            constants = Constants()
            response = requests.get(url = constants.NEWRELIC_API_ENDPOINT,headers= constants.HEADERS, params=data) 
           
        except requests.exceptions.Timeout as e:
            logging.error("Timeout Error: \n {0}".format(e))
        except requests.exceptions.TooManyRedirects as e:
            logging.error("Bad URL: \n {0}".format(e))
        except requests.exceptions.HTTPError as e:
            logging.error("HTTP Error: \n {0}".format(e))
        except requests.exceptions.RequestException as e:
            logging.error("Error occured while connecting to New Relic: \n {0}".format(e))

        return response

    def createDataset(self, Region, days='1'):
        """
        Description : Converting the API response to a dataset

        Parameters : 1. self
                     2. region - the region where instances are to be predicted
                     3. days - number of days of data to be fetched

        Return Value : Pandas dataframe containing the new relic response
        """
        logging.debug("Creating the dataset from New Relic Data")
        logging.debug(days)
        column_names = ['Timestamp','CPU','Instances']
        

        config = configparser.ConfigParser()
        config.read_file(open(r'./app/configuration/properties.conf'))
        clusters = config.get('Region', Region).split(",")
        logging.debug(clusters)
        dataset = {}
        dataset['events']=[]
        
        try:
            data = {}
            data['events']=[]
            try:
                #Getting start and end times to fetch data from New relic
                end = datetime.datetime.now()
                start = end - datetime.timedelta(days=1) 
                end = end.strftime("%Y-%m-%d 08:00")
                start = start.strftime("%Y-%m-%d 08:00")
            except ValueError as e:
                logging.error("DateTime Value Error: {0}\n".format(be))
           
                
            for cluster in clusters:
                
                date_end = datetime.datetime.now()
                date_start = date_end - datetime.timedelta(days=1) 
                end = date_end.strftime("%Y-%m-%d 08:00")
                start = date_start.strftime("%Y-%m-%d 08:00")
                logging.debug(start)
                logging.debug(end)
                i=0
                while i < int(days):
                    query = self.setQuery(start, end, cluster)
                    response = self.sendRequest(query)
                    dataset_response = []
                    dataset_response.append(response)
                    logging.debug(response.text)
                    
                    if response.status_code!=200:
                        logging.error("New Relic Endpoint Could Not Be Accessed. Status Code: {0}\n".format(response.status_code))
                    else :
                        response = json.loads(response.text)

                        
                        
                    

                        #Writing all the records fetched to a dataframe
                        logging.debug("writing to data.csv")
                        for record in response['results'][0]['events']:
                            record['timestamp']= datetime.datetime.utcfromtimestamp(int(record['timestamp']/1000.0))
                            with open('data_'+Region+'.csv', 'a') as f: 
                                
                                w = csv.DictWriter(f, record.keys())
                                w.writerow(record)
                        date_end = date_start
                        date_start = date_end - datetime.timedelta(days=1) 
                        end = date_end.strftime("%Y-%m-%d 08:00")
                        start = date_start.strftime("%Y-%m-%d 08:00")
                        logging.debug(start)
                        logging.debug(end)
                        i+=1
            
                
            data = pd.read_csv('data_'+Region+'.csv')
            data.columns = column_names
            data = data.sort_values(by=['Timestamp'])
            data['Timestamp'] = pd.to_datetime(data['Timestamp'], format='%Y-%m-%d %H:%M:%S')
            data = data.set_index('Timestamp')
            is_1 = data['CPU']==1
            data = data[is_1]
            data = data.drop_duplicates()
            data = data.resample("10T").sum()
            data = data.reset_index()
            data = data[data.CPU != 0]
            logging.debug(data)
            util = COSUtils()
            util.write_dataframe(data, column_names,'getcsvdata', 'data_'+Region+'.csv')
            
            for reponse in dataset_response:
                for record in response['results'][0]['events']:
                    dataset['events'].append(record)
            logging.debug(dataset)
            return dataset
        except ValueError as e: 
            logging.error("JSON Decoding Failed: {0}\n".format(e))
        except KeyError as e: 
            logging.error("Key Not Found in Response: {0}\n".format(e))
        except (NameError, FileNotFoundError) as e:
            logging.error("Error: File Not Found \n {0}".format(e))
        except Exception as e:
            logging.error("Error while writing response to dataframe: {0}\n".format(e))
                
            
            
