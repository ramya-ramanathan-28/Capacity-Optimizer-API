from sklearn.neighbors import KNeighborsRegressor
from sklearn.model_selection import GridSearchCV
from app.models.evaluatedModel import evaluatedModel
import logging
import queue
class KNNRegression():
    def model(self, X_train, y_train, queue):
            #KNN Regressor
        try:
            k_range = list(range(1, 31))
            knn = KNeighborsRegressor()
            param_grid = dict(n_neighbors=k_range)
            KNR = GridSearchCV(knn, param_grid, cv=3).fit(X_train, y_train)
            logging.info("Best Params", KNR.best_params_)
            logging.info("Best Score", KNR.best_score_)
            queue.put(evaluatedModel(KNR.best_score_, KNR.best_estimator_, "KNN Regression"))
        except Exception as e:
            logging.error("KNN Regression error: {0}\n".format(e))
        

    



