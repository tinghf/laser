import optuna
import ray
import os
from model import objective  # Import the objective function


# A Ray remote function to execute one trial of the study
@ray.remote
def evaluate_trial(study_name, storage_url, trial_number):
    # Connect to the existing study
    study = optuna.load_study(study_name=study_name, storage=storage_url)
    trial = study.ask()
    value = objective(trial)
    study.tell(trial, value)
    return value, trial.params

# Main function to set up study and distribute trials
def main(num_trials):
    ray.init()  # Initialize Ray

    # Set up Optuna study with a central storage in MySQL
    storage = "mysql://{}:{}@mysql:3306/{}".format(
        os.environ["MYSQL_USER"],
        os.environ["MYSQL_PASSWORD"],
        os.environ["MYSQL_DATABASE"]
    )
    study_name = "distributed_optuna"
    study = optuna.create_study(study_name=study_name, storage=storage, direction="minimize", load_if_exists=True)

    # List to hold remote function references
    futures = []
    for _ in range(num_trials):
        futures.append(evaluate_trial.remote(study_name, storage, _))

    # Gather all results
    results = ray.get(futures)
    best_result = min(results, key=lambda x: x[0])

    print("Best result: ", best_result)
    ray.shutdown()

if __name__ == "__main__":
    main(100)  # Running 100 trials
