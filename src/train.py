"""Train RF and scaled KNN on an identical stratified Iris holdout."""
import hashlib
import json
import os
import subprocess
from pathlib import Path

import joblib
import mlflow
import pandas as pd
import yaml
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

ROOT = Path(__file__).resolve().parents[1]

def main():
    os.chdir(ROOT)
    params = yaml.safe_load(Path("params.yaml").read_text())
    train = params["train"]
    df = pd.read_csv("data/raw/iris.csv")
    if len(df) != 150 or df.isna().any().any() or set(df.target) != {0, 1, 2}:
        raise ValueError("Invalid Iris data")
    x_train, x_test, y_train, y_test = train_test_split(
        df.drop(columns="target"), df.target, stratify=df.target,
        random_state=train["random_state"], test_size=train["test_size"])
    mlflow.set_tracking_uri(os.environ.get("MLFLOW_TRACKING_URI", "sqlite:///mlflow.db"))
    mlflow.set_experiment("TP_Iris_Classification")
    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    data_hash = hashlib.sha256(Path("data/raw/iris.csv").read_bytes()).hexdigest()
    models = {
        "random_forest": RandomForestClassifier(
            n_estimators=train["n_estimators"], max_depth=train["max_depth"],
            random_state=train["random_state"]),
        "knn": make_pipeline(StandardScaler(), KNeighborsClassifier(**params["knn"]))}
    Path("models").mkdir(exist_ok=True)
    Path("reports").mkdir(exist_ok=True)
    results = {}
    for name, model in models.items():
        with mlflow.start_run(run_name=f"{name}_Iris"):
            mlflow.log_params({"model": name, "test_size": train["test_size"],
                               "random_state": train["random_state"],
                               **({k: train[k] for k in ("n_estimators", "max_depth")}
                                  if name == "random_forest" else params["knn"])})
            mlflow.set_tags({"git_commit": commit, "dataset_sha256": data_hash,
                             "parameters_sha256": hashlib.sha256(Path("params.yaml").read_bytes()).hexdigest()})
            model.fit(x_train, y_train)
            pred = model.predict(x_test)
            metrics = {"accuracy": float(accuracy_score(y_test, pred)),
                       "precision": float(precision_score(y_test, pred, average="weighted", zero_division=0)),
                       "recall": float(recall_score(y_test, pred, average="weighted", zero_division=0)),
                       "f1_score": float(f1_score(y_test, pred, average="weighted", zero_division=0))}
            mlflow.log_metrics(metrics)
            path = f"models/{name}.pkl"
            joblib.dump(model, path)
            mlflow.log_artifact(path, artifact_path="model")
            mlflow.log_artifact("params.yaml")
            results[name] = metrics
    Path("reports/metrics.json").write_text(json.dumps(results, indent=2) + "\n")
    print(json.dumps(results, indent=2))

if __name__ == "__main__":
    main()
