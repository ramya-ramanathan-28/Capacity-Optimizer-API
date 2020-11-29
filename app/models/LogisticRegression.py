class LogisticRegression():
    def model(self, X_train, y_train):
            #LOGISTIC REGRESSION
            params = {
                'penalty':['l1', 'l2'],        # l1 is Lasso, l2 is Ridge
                'solver':['liblinear'],
                'C': np.linspace(0.02,1,10)
            }
            try:    
                lr = LogisticRegression()
                logistic = GridSearchCV(lr, params, cv=3, verbose=2).fit(X_train, y_train)

                logging.info("Logistic Params ", logistic.best_params_)
                logging.info("Logistic Score", logistic.best_score_)
                return evaluatedModel(logistic.best_score_, logistic.best_score_, "Logistic Regression")
            except UndefinedMetricWarning as e:
                logging.error("Undefined metric: {0}\n".format(e))
            except DataDimensionalityWarning as e:
                logging.error("Dimensionality Warning: {0}\n".format(e))
            except Exception as e:
                logging.error("Logistic Regression error: {0}\n".format(e))
            