from flask import Flask
from flask_restplus import Api, Resource, fields, reqparse

app = Flask(__name__)
app.config['BUNDLE_ERRORS'] = True #Enable bundling of errors to display all the missing parameters
api = Api(app, catch_all_404s=True, ui=False)

from app import CapacityOptimizerAPI, RegressionSelector