# cnnClassifier/pipeline/stage_04_evaluation.py
from cnnClassifier.config.configuration import ConfigurationManager
from cnnClassifier.components.model_evaluation import Evaluation
from cnnClassifier import logger

STAGE_NAME = "Evaluation stage"

class EvaluationPipeline:
    def __init__(self):
        pass

    def main(self):
        config = ConfigurationManager()
        eval_config = config.get_evaluation_config()
        evaluation = Evaluation(eval_config)
        
        # Step 1: Evaluate
        evaluation.evaluation()
        
        # Step 2: Save score
        evaluation.save_score()
        
        # Step 3: Log to MLflow (LOCAL + DAGSHUB) ✓ UNCOMMENTED
        evaluation.log_into_mlflow()

if __name__ == '__main__': 
    try:
        logger. info(f"*******************")
        logger.info(f">>>>>> stage {STAGE_NAME} started <<<<<<")
        obj = EvaluationPipeline()
        obj.main()
        logger.info(f">>>>>> stage {STAGE_NAME} completed <<<<<<\n\nx==========x")
    except Exception as e:
        logger.exception(e)
        raise e