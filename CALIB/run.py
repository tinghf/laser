import subprocess
import sys
import os
from pathlib import Path

import optuna
from mysql_storage import get_storage_url
from objective import objective

# Run Optuna optimization
# study = optuna.create_study(direction="minimize")
# storage_url = get_storage_url()
# storage_url = "sqlite:///optuna_study.db"  # SQLite file-based DB
storage_url = "mysql://{}:{}@mysql:3306/{}".format(
    os.environ["MYSQL_USER"],
    os.environ["MYSQL_PASSWORD"],
    os.environ["MYSQL_DB"]
)

# You can use non-default samplers if you want; we'll go with the default
# sampler = optuna.samplers.CmaEsSampler()
# optuna.delete_study(study_name="spatial_demo_calibr8n", storage=storage_url)
study = optuna.load_study(
    # sampler=sampler,
    storage=storage_url,
    study_name="spatial_demo_calibration_on_aks4"
)
study.optimize(objective, n_trials=2)  # n_trials is how many more trials; it will add to an existing study if it finds it in the db.


# Print the best parameters
print("Best parameters:", study.best_params)

# laser_script = Path("impatient.py").resolve(strict=True)
# subprocess.run([sys.executable, str(laser_script)], check=True)
