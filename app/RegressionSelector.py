import requests 
from flask import abort 
import queue
from operator import attrgetter
from app.constants import Constants
from app.models.DecisionTreeRegression import DecisionTreeRegression
from app.models.KNNRegression import KNNRegression
from app.models.AdaboostRegression import AdaboostRegression
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



	
class RegressionSelector():
	def __init__(self):
		"""
		Description : Constructor to class RegressionSelector

		Parameters : 1. self

		"""
		self.bestModel = None
		self.models = None

	def getResponse(self):
		"""
		Description : Creates the response json containing the scores of all models and the best model

		Parameters : 1. self

		Return Value : Returns the response as a dictionary
		"""
		try:
			data = {}
			for model in self.models:
				data[model.modelName]=model.score
			data['Best Model'] = self.bestModel.modelName
			data['Best Score'] = self.bestModel.score
			return data
		except Exception as e:
			logging.error("Json generation Error: {0}\n".format(e))

	def runInParallel(self, fns, X_train, y_train):
		"""
		Description : Runs all models in parallel and returns their scores

		Parameters : 1. self
					 2. fns - models to run in parallel
					 3. X_train - feature set to train
					 4. y_train - target fields to be used for training

		Return Value : Returns the scores of all the models
		"""
		threads = []
		scores = []
		try:
			que = queue.Queue()
			for fn in fns:
				args = ( X_train, y_train, que)
				t = Thread(target = fn.model, args = args)
				t.start()
				threads.append(t)
			for t in threads:
				t.join() 
			while not que.empty():
				result = que.get()
				scores.append(result) 
			return scores
		except Exception as e:
			logging.error("Threading Exception: {0}\n".format(e))

	def gridSearch(self, X_train, y_train):
		"""
		Description : Finds the R2 scores of all models in parallel

		Parameters : 1. self
					 2. X_train - feature set to train
					 3. y_train - target fields to be used for training

		"""
		logging.info("gridSearch")
		decisionTree = DecisionTreeRegression()
		knn = KNNRegression()
		adaboost = AdaboostRegression()
		
		#self.runInParallel([self.logisticRegression, self.linearRegression, self.randomForest, self.gradientBoost, self.SVM, self.KNN, self.decisionTree, self.adaboost], mutex, args)
		self.models = self.runInParallel([decisionTree, knn, adaboost], X_train, y_train)
		self.bestModel = self.Score(self.models)
		

	def Score(self, models):
		"""
		Description : Finds the model having the best score

		Parameters : 1. self
					 2. models - list of objects of evaluatedModel Class

		Return Value : Returns the model as an object of evaluatedModel Class
		"""
		try:
			bestModel = max(models, key=attrgetter('score'))
			return bestModel
		except KeyError as e:
			logging.error("Key not found in dataset: {0}\n".format(e))
		except ArithmeticError as e:
			logging.error("Arithmetic exception: {0}\n".format(e))
		except Exception as e:
			logging.error("Error during scoring: {0}\n".format(e))

		


		
	   


		



