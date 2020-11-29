import requests 
from flask import abort 
import queue
from operator import attrgetter
from app.constants import Constants
from app.models.DecisionTreeRegression import DecisionTreeRegression
from app.models.KNNRegression import KNNRegression
from app.models.AdaboostRegression import AdaboostRegression
from app.RegressionSelector import RegressionSelector
from app.DataIngestion import NewRelicDataIngestion
from app.COSUtils import COSUtils
from flask_restplus import reqparse
from sklearn.linear_model import LogisticRegression, LinearRegression
from sklearn.ensemble import RandomForestRegressor,GradientBoostingRegressor, AdaBoostRegressor
from sklearn.model_selection import train_test_split, cross_val_score, cross_val_predict, GridSearchCV
from sklearn.tree import DecisionTreeRegressor
from sklearn.neighbors import KNeighborsRegressor
from threading import Thread, Lock
from warnings import simplefilter
import ibm_boto3
from ibm_botocore.client import Config
from botocore.exceptions import ClientError
simplefilter(action='ignore', category=FutureWarning)
simplefilter(action='ignore', category=DeprecationWarning)
from numpy import array
import pandas as pd
import numpy as np
import os
from sklearn import metrics, svm
import threading
import time, json
import urllib
import csv
import datetime
from numpy.random import seed
import logging 
seed(500)

constants = Constants()
class FeedbackLoop():
	
	def __init__(self):
		"""
		Description : Constructor to class FeedbackLoop, initializes the connection to COS

		Parameters : 1. self

		"""
		constants = Constants()
		self.client = ibm_boto3.client(service_name='s3',ibm_api_key_id=constants.API_KEY,ibm_auth_endpoint=constants.AUTH_ENDPOINT,config=Config(signature_version='oauth'),endpoint_url=constants.COS_API_ENDPOINT)
		column_names = ['Timestamp','CPU','Instances']
		util = COSUtils()
		self.bucketName = 'getcsvdata'
		self.data = {}
		self.score = {}
		self.modelSelector = {}
		self.response = {}
		for region in ['Dallas', 'London', 'Tokyo']:
			self.initialDataset = 'initial_'+region+'.csv'
			self.fetchedDataset = 'data_'+region+'.csv'
			
			self.data[region] = util.get_dataframe(column_names,  self.bucketName, self.initialDataset)
			self.data[region].columns = column_names

			self.data[region] = self.convertTimestampToFloat(self.data[region])
			self.modelSelector[region] = RegressionSelector()
			self.score[region] = self.getScore(self.data[region], region)['Best Score']
		logging.info("Score:" + str(self.score[region]))
		logging.debug("Response:")
		logging.debug(self.response)

	def getResponse(self, region):
		"""
		Description : Returns the JSON response

		Return value : 1. JSON response as a dict
					   2. Region 
		
		"""
		return self.response[region]

	def getScore(self, series, region):
		"""
		Description : Selects the best model and returns its score 

		Parameters : 1. self
					 2. series - selects best score 
					 3. region - the region where instances are to be predicted

		"""
		X_train = series['date'].values
		X_train = X_train.reshape(-1, 1)
		y_train = series['Instances']
		self.modelSelector[region].gridSearch(X_train, y_train)
		self.response[region] = self.modelSelector[region].getResponse()
		return self.response[region]
		

	def setScore(self, score):
		"""
		Description : Set score based on parameter

		Parameters : 1. self
					 2. score - score to be set for the class

		"""
		self.score[region] = score

	def returnScore(self):
		"""
		Description : Returns the score 

		Parameters : 1. self

		Return Value : score of the current model
		"""
		return self.response['Best Score']
	
	def getModel(self, X, region):
		"""
		Description : Returns the best model and predictions of all the models

		Parameters : 1. self
					 2. The feature set to make the prediction
					 3. region - the region where instances are to be predicted

		Return Value : returns the best model
		"""
		data = {}
		for model in self.modelSelector[region].models:
			y = model.model.predict(X)
			data[model.modelName] = str(y[0])

			

		data['Best Model'] = self.response[region]['Best Model']
		return data
		

	def parser(self, x):
		"""
		Description : parses the date into a specific format

		Parameters : 1. self
					 2. x

		Return Value : returns datetime parsed datetime
		"""
		return pd.datetime.strptime(x, '%Y-%m-%d %H:%M:%S')

	def convertTimestampToFloat(self, series):
		"""
		Description : coverting data of timestamp type to float type

		Parameters : 1. self
					 2. series - dataframe containing a Timestamp column

		Return Value : returns dataframe after conversion
		"""
		logging.info("converting Timestamp series to Float")
		try: 
			series = series.drop(['CPU'], axis=1)
			series['Timestamp'] = pd.to_datetime(series['Timestamp'])  
			min_val=pd.to_datetime('2019-02-18 00:00:05')
			delta = np.timedelta64(1,'D')
			series['date'] = (series['Timestamp'] - min_val) / delta
		except ValueError as e:
			logging.error("DateTime Value Error: {0}\n".format(e))
		except Exception as e:
			logging.error("DateTime Error: {0}\n".format(e))
		return series

	def feedback(self, region):
		"""
		Description : updating model and score based on new fetched data

		Parameters : 1. self
					 2. region - the region where instances are to be predicted
		"""
		logging.info("Entered feedback of Feedback Loop")
		self.initialDataset = "initial_"+region+".csv"
		self.fetchedDataset = "data_"+region+".csv"

		try:
			util = COSUtils()
			column_names = ['Timestamp','CPU','Instances']
			dataset = NewRelicDataIngestion()
			dataset.createDataset(region)
			logging.debug("Fetched dataset")
			fetchedData = util.get_dataframe(column_names, self.bucketName, self.fetchedDataset)
			logging.debug(self.data)
			fetchedData = self.convertTimestampToFloat(fetchedData)
			fetchedData = self.data[region].append(fetchedData)
			logging.debug(fetchedData)
			score = self.getScore(fetchedData, region)['Best Score']
			logging.debug(score)
			if score > self.score[region]:
				logging.info("New Score:" + str(score))
				self.score[region] = score
				initial = util.get_dataframe(column_names, self.bucketName, self.initialDataset)
				data = util.get_dataframe(column_names, self.bucketName, self.fetchedDataset)
				initial = initial.append(data)
				initial = initial.drop_duplicates()
				initial = initial[initial.CPU != 0]
				util.write_dataframe(initial, column_names,self.bucketName, self.initialDataset)
				df = pd.DataFrame( columns=column_names)
				util.write_dataframe(df, column_names, self.bucketName, self.fetchedDataset)
		except Exception as e:
			logging.error("Error during score comparison: {0}\n".format(e))
			

