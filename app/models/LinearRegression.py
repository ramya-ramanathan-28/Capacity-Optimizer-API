class LinearRegression():
    def model(self, X_train, y_train):
        #LINEAR REGRESSION
        try:
            model = LinearRegression()
            parameters = {'fit_intercept':[True,False], 'normalize':[True,False], 'copy_X':[True, False]}
            linear = GridSearchCV(model, parameters, cv=3).fit(X_train, y_train)
        
            logging.info("Linear Params", linear.best_params_)
            logging.info("Linear Score", linear.best_score_)
            return evaluatedModel(linear.best_score_, linear.best_score_, "Linear Regression")
        except UndefinedMetricWarning as e:
            logging.error("Undefined metric: {0}\n".format(e))
        except DataDimensionalityWarning as e:
            logging.error("Dimensionality Warning: {0}\n".format(e))
        except Exception as e:
            logging.error("Logistic Regression error: {0}\n".format(e))
       
    