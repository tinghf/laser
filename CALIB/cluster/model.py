def objective(trial):
    x = trial.suggest_float("x", -10, 10)
    return (x - 2) ** 2
