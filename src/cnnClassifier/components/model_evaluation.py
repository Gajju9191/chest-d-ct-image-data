# cnnClassifier/components/model_evaluation.py
import os
import tensorflow as tf
from pathlib import Path
import mlflow
import mlflow.keras
from urllib.parse import urlparse
from cnnClassifier.entity. config_entity import EvaluationConfig
from cnnClassifier.utils.common import read_yaml, create_directories, save_json


class Evaluation:
    def __init__(self, config: EvaluationConfig):
        self.config = config

    def _valid_generator(self):
        datagenerator_kwargs = dict(
            rescale=1./255,
            validation_split=0.30
        )

        dataflow_kwargs = dict(
            target_size=self. config.params_image_size[:-1],
            batch_size=self.config.params_batch_size,
            interpolation="bilinear"
        )

        valid_datagenerator = tf.keras.preprocessing.image. ImageDataGenerator(
            **datagenerator_kwargs
        )

        self.valid_generator = valid_datagenerator.flow_from_directory(
            directory=self.config.training_data,
            subset="validation",
            shuffle=False,
            **dataflow_kwargs
        )

    @staticmethod
    def load_model(path: Path) -> tf.keras.Model:
        return tf.keras.models.load_model(path)

    def evaluation(self):
        self.model = self.load_model(self.config.path_of_model)
        self._valid_generator()
        self.score = self.model.evaluate(self.valid_generator)
        self.save_score()

    def save_score(self):
        scores = {"loss": self. score[0], "accuracy": self.score[1]}
        save_json(path=Path("scores.json"), data=scores)

    def log_into_mlflow(self):
        """
        Log model, metrics, and parameters to MLflow (LOCAL + DAGSHUB)
        CRITICAL: Set both tracking_uri AND registry_uri
        """
        
        # ========== Set credentials ==========
        os.environ["MLFLOW_TRACKING_USERNAME"] = "Gajju9191"
        os.environ["MLFLOW_TRACKING_PASSWORD"] = "089e1f4ec33ad67cc8541160fe89a199ce77186d"
        
        # ========== Prepare data ==========
        metrics = {
            "loss": float(self.score[0]),
            "accuracy": float(self. score[1])
        }
        
        print("\n" + "="*80)
        print("MLflow LOGGING:  LOCAL + DAGSHUB")
        print("="*80)
        
        # ========== LOG TO LOCAL MLFLOW ==========
        try:
            print("\n[1/2] Logging to LOCAL MLflow...")
            
            mlflow.set_tracking_uri("file:///$(pwd)/mlruns")
            mlflow.set_registry_uri("file:///$(pwd)/mlruns")
            mlflow.set_experiment("CNN_Image_Classification")
            
            with mlflow.start_run(run_name="Model_Evaluation_v1") as local_run:
                local_run_id = local_run.info.run_id
                
                mlflow.log_params(self.config.all_params)
                mlflow.log_metrics(metrics)
                mlflow.set_tag("framework", "tensorflow")
                mlflow.set_tag("model_type", "CNN")
                
                mlflow.keras.log_model(
                    self.model,
                    "model",
                    registered_model_name="CNNClassifier"
                )
                
                print(f"   ✓ Run ID: {local_run_id}")
                print(f"   ✓ Location: mlruns/ (your machine)")
                print(f"   ✓ Model Registered: CNNClassifier")
        
        except Exception as e:
            print(f"   ✗ Error:  {e}")
            local_run_id = None
        
        # ========== LOG TO DAGSHUB REMOTE ==========
        try:
            print("\n[2/2] Logging to DAGSHUB Remote...")
            
            # ✓✓✓ CRITICAL: Set BOTH tracking_uri AND registry_uri ✓✓✓
            mlflow.set_tracking_uri(self.config.mlflow_tracking_uri)
            mlflow.set_registry_uri(self.config.mlflow_registry_uri)
            mlflow.set_experiment("CNN_Image_Classification")
            
            with mlflow.start_run(run_name="Model_Evaluation_v1") as remote_run:
                remote_run_id = remote_run.info.run_id
                
                mlflow.log_params(self.config.all_params)
                mlflow.log_metrics(metrics)
                mlflow.set_tag("framework", "tensorflow")
                mlflow.set_tag("model_type", "CNN")
                mlflow.set_tag("repository", "dagshub")
                
                mlflow.keras.log_model(
                    self. model,
                    "model",
                    registered_model_name="CNNClassifier"
                )
                
                print(f"   ✓ Run ID: {remote_run_id}")
                print(f"   ✓ Location:  Dagshub Cloud")
                print(f"   ✓ Model Registered:  CNNClassifier")
        
        except Exception as e:
            print(f"   ✗ Error: {e}")
            print(f"   ⚠ Check credentials and internet connection")
            remote_run_id = None
        
        # ========== SUMMARY ==========
        print("\n" + "="*80)
        if local_run_id and remote_run_id:
            print("✓ SUCCESSFULLY LOGGED TO BOTH!")
            print("="*80)
            print(f"\n📊 View Results:\n")
            print(f"   LOCAL MLflow:")
            print(f"   ├─ Run ID: {local_run_id}")
            print(f"   ├─ View:  http://localhost:5000")
            print(f"   └─ Command: mlflow ui\n")
            print(f"   DAGSHUB Remote:")
            print(f"   ├─ Run ID: {remote_run_id}")
            print(f"   └─ View: https://dagshub.com/Gajju9191/chest-ct-image-data/mlflow")
        else:
            print("⚠ PARTIAL SUCCESS")
            print("="*80)
            print(f"Local:  {local_run_id if local_run_id else 'Failed'}")
            print(f"Dagshub: {remote_run_id if remote_run_id else 'Failed'}")
        
        print("="*80 + "\n")