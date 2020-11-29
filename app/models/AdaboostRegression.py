from sklearn.ensemble import AdaBoostRegressor
from sklearn.model_selection import GridSearchCV
from sklearn.tree import DecisionTreeRegressor
from app.models.evaluatedModel import evaluatedModel
import logging
import queue
class AdaboostRegression():
    def model(self, X_train, y_train, queue):
        #ADABOOST
        try:
            param_grid = {

                        "base_estimator__splitter" :   ["best", "random"],
                        "n_estimators": [1, 2]
                        }


            DTR = DecisionTreeRegressor(random_state = 11, max_features = "auto",  max_depth = None)

            ABR = AdaBoostRegressor(base_estimator = DTR)

            # run grid search
            adaboost = GridSearchCV(ABR, param_grid=param_grid, cv=3).fit(X_train, y_train)
            logging.info("Best Params", adaboost.best_params_)
            logging.info("Best Score", adaboost.best_score_)
            queue.put(evaluatedModel(adaboost.best_score_, adaboost.best_estimator_, "Adaboost Regression"))
        except Exception as e:
            logging.error("Adaboost Regression error: {0}\n".format(e))
        
            