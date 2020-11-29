class GradientBoostRegression():
    def model(self, X_train, y_train):
        #GradientBoostRegression
        try:
            estimator = GradientBoostingRegressor()
            param_grid={'n_estimators':[100, 200], 'learning_rate': [0.1, 0.05, 0.02, 0.01], 'max_depth':[4, 6], 'min_samples_leaf':[3,5,9,17] } 
            gradient = GridSearchCV(estimator=estimator, cv=3, param_grid=param_grid).fit(X_train, y_train)
            logging.info("Best Params", gradient.best_params_)
            logging.info("Best Score", gradient.best_score_)
            return evaluatedModel(gradient.best_score_, gradient.best_score_, "Gradient Boost Regression")
        except UndefinedMetricWarning as e:
            logging.error("Undefined metric: {0}\n".format(e))
        except DataDimensionalityWarning as e:
            logging.error("Dimensionality Warning: {0}\n".format(e))
        except Exception as e:
            logging.error("Logistic Regression error: {0}\n".format(e))
        

        