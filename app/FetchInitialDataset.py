import configparser
import datetime
import json
import requests
import csv
import os
import pandas as pd
import numpy as np

# THIS IS A PYTHON SCRIPT TO FETCH THE INITIAL DATA TO BE UPLOADED IN COS
class FetchInitialDataset():
    def getDataset(self):
            """
            Description : Getting Initial Datasets for all regions

            Parameters : 1. self
            
            Return Value : Stores the dataset in the form of a csv file
            """
            config = configparser.ConfigParser()
            config.read_file(open(r'./configuration/properties.conf'))
            for region in ['Dallas', 'London', 'Tokyo']:
                clusters = config.get('Region', region).split(",")
                for cluster in clusters:
                    logging.debug(region)
                    logging.debug(clusterName)
                    date_end = datetime.datetime.now()
                    date_start = date_end - datetime.timedelta(days=1) 
                    end = date_end.strftime("%Y-%m-%d 08:00")
                    start = date_start.strftime("%Y-%m-%d 08:00")
                    i=0
                    while i <= 30:
                        logging.debug(i)
                        nrql='''SELECT cpuRequestPerPod,instances from dataplane_capacity where clusterID=\''''+clusterName+'''\' since \'''' + start + '''\' until \'''' + end +  '''\' limit 1000 order by timestamp'''
                        data = {"nrql":nrql} 

                        response = requests.get(url = '''https://insights-api.newrelic.com/v1/accounts/1931257/query''',headers= {'Accept': 'application/json', 'X-Query-Key': 'W_AaITc2G-tSYfaVRHe5aPZcDyhx6x7w'}, params=data) 

                        response = json.loads(response.text)
                        for record in response['results'][0]['events']:
                            record['timestamp']= datetime.datetime.utcfromtimestamp(int(record['timestamp']/1000.0))
                            with open('initial_'+region+'.csv', 'a') as f: 
                                w = csv.DictWriter(f, record.keys())
                                w.writerow(record)
                        i += 1
                        date_end = date_start
                        date_start = date_end - datetime.timedelta(days=1) 
                        end = date_end.strftime("%Y-%m-%d 08:00")
                        start = date_start.strftime("%Y-%m-%d 08:00")
                        logging.debug(start)
                df = pd.read_csv("initial_"+region+".csv")
                os.remove("initial_"+region+".csv")
                df.columns = ['Timestamp', 'CPU', 'Instances']
                df = df.sort_values(by=['Timestamp'])
                df['Timestamp'] = pd.to_datetime(df['Timestamp'], format='%Y-%m-%d %H:%M:%S')
                df = df.drop_duplicates()
                df = df.set_index('Timestamp')
                is_1 = df['CPU']==1
                df = df[is_1]
                df = df.resample("10T").sum()
                df = df.reset_index()
                df = df[df.CPU != 0]
                
                df.to_csv("initial_"+region+".csv")
                


    

if __name__ == "__main__":
    dataset = FetchInitialDataset()
    dataset.getDataset()