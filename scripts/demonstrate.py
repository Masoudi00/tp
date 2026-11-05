"""Verify restoration and forced retraining in an isolated local clone."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

root = Path(__file__).resolve().parents[1]
clone = root / (sys.argv[1] if len(sys.argv) > 1 else "reproduction-clone")
if clone.exists():
    raise SystemExit("reproduction-clone already exists; use a fresh destination")
env = os.environ.copy()
env["PATH"] = str(Path(sys.executable).parent) + os.pathsep + env["PATH"]
env["DVC_SITE_CACHE_DIR"] = str(root / ".dvc/site-cache")
env["MLFLOW_DISABLE_AGENT_HINT"] = "1"

def run(*args, cwd=clone):
    result = subprocess.run(args, cwd=cwd, env=env, text=True, capture_output=True)
    if result.returncode:
        raise RuntimeError(f"{args}: {result.stdout}\n{result.stderr}")
    return result.stdout

run("git", "clone", "--no-local", str(root), str(clone), cwd=root)
run("git", "checkout", "v1.0")
run("dvc", "remote", "modify", "--local", "storage", "url", str(root / "dvc-storage"))
run("dvc", "pull")
baseline = json.loads((clone / "reports/metrics.json").read_text())
wine = clone / "data/raw/wine.csv"
original = hashlib.sha256(wine.read_bytes()).hexdigest()
wine.write_bytes(wine.read_bytes() + b"\n")
run("dvc", "add", "data/raw/wine.csv")
modified = hashlib.sha256(wine.read_bytes()).hexdigest()
run("git", "restore", "data/raw/wine.csv.dvc")
run("dvc", "checkout", "data/raw/wine.csv.dvc", "--force")
restored = hashlib.sha256(wine.read_bytes()).hexdigest()
assert modified != original == restored
run("dvc", "repro", "--force", "--no-run-cache")
reproduced = json.loads((clone / "reports/metrics.json").read_text())
assert reproduced == baseline
run(sys.executable, "scripts/validate.py")
status = run("dvc", "status")
report = {"environment": "Separate clone and empty DVC cache; same Python environment and machine",
          "tag": "v1.0", "wine_original_sha256": original,
          "wine_modified_sha256": modified, "wine_restored_sha256": restored,
          "data_restoration_passed": True, "forced_training_metrics_equal": True,
          "baseline_metrics": baseline, "dvc_status": status.strip()}
(root / "reports/reproduction.json").write_text(json.dumps(report, indent=2) + "\n")
print(json.dumps(report, indent=2))
