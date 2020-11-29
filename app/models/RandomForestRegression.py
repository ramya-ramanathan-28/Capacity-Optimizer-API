class RandomForestRegression():
    def model(self, X_train, y_train):
        #RANDOM FOREST
        try:
            param_grid = {
                'bootstrap': [True],
                'max_depth': [80, 100],
                'min_samples_leaf': [3, 4, 5],
                'min_samples_split': [8, 10, 12],
                'n_estimators': [100, 200, 300]
            }
            # Create a based model
            rf = RandomForestRegressor()
            # Instantiate the grid search model
            randomForest = GridSearchCV(estimator = rf, param_grid = param_grid, cv = 3).fit(X_train, y_train)
            logging.info("Best Params", randomForest.best_params_)
            logging.info("Best Score", randomForest.best_score_)
            return evaluatedModel(randomForest.best_score_, randomForest.best_score_, "Random Forest Regression")
        except UndefinedMetricWarning as e:
            logging.error("Undefined metric: {0}\n".format(e))
        except DataDimensionalityWarning as e:
            logging.error("Dimensionality Warning: {0}\n".format(e))
        except Exception as e:
            logging.error("Logistic Regression error: {0}\n".format(e))
        
        