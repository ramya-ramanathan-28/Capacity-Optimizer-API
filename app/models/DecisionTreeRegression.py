from sklearn.tree import DecisionTreeRegressor
from app.models.evaluatedModel import evaluatedModel
import logging
from sklearn.model_selection import GridSearchCV
import queue
class DecisionTreeRegression():
    def __init__(self):
        logging.info("Entered __init__ Decision Tree")
    def model(self, X_train, y_train, queue):
        #DECISION TREE
        try:
            logging.info("Entered Decision Tree")
            decision_tree = DecisionTreeRegressor()

            parameter_grid = {'max_depth': [5, 10, 15],'min_samples_leaf':[3,5,9,17]}
            decision = GridSearchCV(decision_tree, param_grid = parameter_grid,cv = 3).fit(X_train,y_train)
            logging.info("Best Params", decision.best_params_)
            logging.info("Best Score", decision.best_score_)
            queue.put(evaluatedModel(decision.best_score_, decision.best_estimator_, "Decision Tree Regression"))
        except Exception as e:
            logging.error("Decision Tree Regression error: {0}\n".format(e))
        
        