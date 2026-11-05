import json
import joblib
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import yaml

params = yaml.safe_load(open("params.yaml"))["train"]
frame = pd.read_csv("data/raw/iris.csv")
_, x, _, y = train_test_split(frame.drop(columns="target"), frame.target,
    test_size=params["test_size"], random_state=params["random_state"], stratify=frame.target)
metrics = json.load(open("reports/metrics.json"))
for name in ("random_forest", "knn"):
    model = joblib.load(f"models/{name}.pkl")
    assert accuracy_score(y, model.predict(x)) == metrics[name]["accuracy"]
    assert metrics[name]["accuracy"] >= 0.85
    assert all(0 <= value <= 1 for value in metrics[name].values())
print("Both saved models reproduce the recorded holdout accuracy and pass the 0.85 threshold.")
