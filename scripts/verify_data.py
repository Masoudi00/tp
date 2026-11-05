"""Validate regenerated data against the committed DVC manifests."""
import hashlib
from pathlib import Path
import yaml

for name in ("iris", "wine"):
    path = Path(f"data/raw/{name}.csv")
    expected = yaml.safe_load(Path(str(path) + ".dvc").read_text())["outs"][0]["md5"]
    actual = hashlib.md5(path.read_bytes()).hexdigest()
    assert actual == expected, (name, actual, expected)
    print(f"{name}: DVC content hash verified")
