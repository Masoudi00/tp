"""Generate two offline datasets shipped with scikit-learn."""
from pathlib import Path
from sklearn.datasets import load_iris, load_wine

def main():
    root = Path(__file__).resolve().parents[1]
    output = root / "data/raw"
    output.mkdir(parents=True, exist_ok=True)
    for name, loader in (("iris", load_iris), ("wine", load_wine)):
        frame = loader(as_frame=True).frame
        assert not frame.isna().any().any()
        frame.to_csv(output / f"{name}.csv", index=False, lineterminator="\n")
        print(f"{name}: {len(frame)} observations, {frame.shape[1]-1} variables")

if __name__ == "__main__":
    main()
