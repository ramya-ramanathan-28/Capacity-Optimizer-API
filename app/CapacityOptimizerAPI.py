import flask
from flask import Flask, request 
from flask_restplus import Api, Resource, reqparse
import json 
import numpy as np
from app import api 
from app import app
from app.FeedbackLoop import FeedbackLoop
from app.DataIngestion import NewRelicDataIngestion
import logging
feedbackObject = FeedbackLoop()
score = None

@app.route('/train', methods=['POST'])
def model():
    """
    Description : API endpoint to get the train and update the model

    Return Value : Returns a JSON response containing R2 scores of different models and the best model
    """
    region= request.args.get('region')
    feedbackObject.feedback(region)
    score = feedbackObject.getResponse(region)

    if score!=None:
        response = score
    else :
        response = { "Message" : "Failure to retrieve score" }
    return flask.jsonify(response)

@app.route('/predict', methods=['GET'])
def predict():
    """
    Description : API endpoint to get the predicted value for a given feature value

    Return Value : Returns a JSON response containing target value by different models
    """
    X = request.args.get('X')
    region = request.args.get('Region')
    modelResponse = feedbackObject.getModel(np.array(float(X)).reshape(1, -1), region)  
    if modelResponse!=None:
        response = modelResponse
    else :
        response = { "Message" : "Failure to get target" }
    return flask.jsonify(response)

@app.route('/fetch', methods=['GET'])
def fetch():
    """
    Description : API endpoint to get the Daily New Relic Data for the specified cluster name

    Return Value : Returns a JSON response containing the data record fields
    """
    region = request.args.get('Region')
    days = request.args.get('Days')
    logging.debug("Region Name: {0}\n".format(region))

    #REGION AND NUMBER OF RECORDS
    dataIngest = NewRelicDataIngestion()
    response = dataIngest.createDataset(region, days)
    
    return flask.jsonify(response)