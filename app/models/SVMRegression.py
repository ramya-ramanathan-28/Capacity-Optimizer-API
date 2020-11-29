class SVMRegression():
    def model(self, X_train, y_train):
            #SVM REGRESSION 
        try:
            Cs = [0.001, 0.01, 0.1, 1, 10]
            gammas = [0.001, 0.01, 0.1, 1]
            param_grid = {'C': Cs, 'gamma' : gammas}
            svr = GridSearchCV(svm.SVC(kernel='rbf'), param_grid, cv=3).fit(X_train, y_train)
            logging.info("Best Params", svr.best_params_)
            logging.info("Best Score", svr.best_score_)
            return evaluatedModel(svr.best_score_, svr.best_score_, "SVM Regression")
        except UndefinedMetricWarning as e:
            logging.error("Undefined metric: {0}\n".format(e))
        except DataDimensionalityWarning as e:
            logging.error("Dimensionality Warning: {0}\n".format(e))
        except Exception as e:
            logging.error("Logistic Regression error: {0}\n".format(e))
        
    