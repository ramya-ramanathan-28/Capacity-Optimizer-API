# Capacity Optimizer API
## Using Cloud Foundry to host the REST API

The files that are required to host a REST API are as follows:

- manifest.yml: Used to specify the memory required by the application, the command to initiate the API, and the ports to be exposed 
- requirements.txt: The required packages to be installed on cloud foundry
- runtime.txt: Specifies the python version to be run

```bash
$ ibmcloud login --sso
$ ibmcloud target --cf -o <org> -s <space>
$ ibmcloud cf push
```
The API generates and returns a route that can be used to access it such as  https://capacityoptimizer-balanced-gerenuk.eu-gb.mybluemix.net

## Endpoints provided for the API 

### Train 
- This endpoint is used to train and update the model. 
- It fetches the data from New Relic, and checks if the model improves with the addition of the new data, and updates the model.
- It returns the scores of different models, and also identifies the best model.
- This endpoint requires region - Dallas, Tokyo or London as input parameter
#### Command:
```
$  curl -X POST  https://capacityoptimizer-appreciative-klipspringer.eu-gb.mybluemix.net/train?Region=Dallas -H 'Content-Type: application/json' 
```
#### Response JSON:
```json
{
    "Adaboost Regression": -0.3402342814196262,
    "Best Model": "Adaboost Regression",
    "Best Score": -0.3402342814196262,
    "Decision Tree Regression": -0.36750189763937274,
    "KNN Regression": -0.3509784909726898
}
```

### Fetch 
- This endpoint is used to fetch data from New Relic on specification of region and the number of days of data that is required.
#### Command:
```
$  curl -X GET  https://capacityoptimizer-appreciative-klipspringer.eu-gb.mybluemix.net/fetch?Region=Tokyo\&Days=30 -H 'Content-Type: application/json' 
```
#### Response JSON:
```json
{
    "events": [
        {
            "cpuRequestPerPod": "3",
            "instances": "180",
            "timestamp": 1557129671462
        },
        {
            "cpuRequestPerPod": "1",
            "instances": "606",
            "timestamp": 1557129673673
        },
        {
            "cpuRequestPerPod": "2",
            "instances": "297",
            "timestamp": 1557129676023
        },
        {
            "cpuRequestPerPod": "2",
            "instances": "300",
            "timestamp": 1557130233375
        },
        {
            "cpuRequestPerPod": "1",
            "instances": "609",
            "timestamp": 1557130236129
        },
        {
            "cpuRequestPerPod": "3",
            "instances": "181",
            "timestamp": 1557130237984
        }
    ]
}
```

### Predict 
- This endpoint is used to get the target values using various models,based on the feature and region given as input. 
#### Command:
```
$  curl -X GET  https://capacityoptimizer-balanced-gerenuk.eu-gb.mybluemix.net/predict?X=60.0&Region=Dallas -H 'Content-Type: application/json' 
```
#### Response JSON:
```json
{
    "Adaboost Regression": "539.0",
    "Best Model": "Adaboost Regression",
    "Decision Tree Regression": "525.7619047619048",
    "KNN Regression": "536.7777777777778"
}
```



