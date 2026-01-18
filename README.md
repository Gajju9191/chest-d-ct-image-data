# chest-d-ct--image-data


import dagshub
dagshub.init(repo_owner='Gajju9191', repo_name='chest-d-ct-image-data', mlflow=True)

import mlflow
with mlflow.start_run():
  mlflow.log_param('parameter name', 'value')
  mlflow.log_metric('metric name', 1)


https://dagshub.com/Gajju9191/chest-d-ct-image-data.mlflow

export MLFLOW_TRACKING_URI="https://dagshub.com/Gajju9191/chest-ct-mlflow-fixed.mlflow"

export MLFLOW_TRACKING_USERNAME="Gajju9191"

export MLFLOW_TRACKING_PASSWORD="089e1f4ec33ad67cc8541160fe89a199ce77186d"



### DVC cmd

dvc init

dvc repro

dvc dag