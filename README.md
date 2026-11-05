# TP Git DVC MLflow

Le but du TP est de classer les fleurs Iris avec Random Forest et KNN, puis de garder une trace du code, des données et des résultats. Wine sert de deuxième dataset pour tester DVC.

## Lancer le projet

Avec Python 3.12, dans PowerShell :

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.lock.txt
$env:DVC_SITE_CACHE_DIR="$PWD\.dvc\site-cache"
python src/prepare_data.py
python scripts/verify_data.py
dvc repro --force
python scripts/validate.py
mlflow ui --backend-store-uri sqlite:///mlflow.db
```

Ouvrir http://127.0.0.1:5000 puis **Model training → TP_Iris_Classification**.

## Résultats

Même découpage pour les deux modèles : 120 fleurs pour apprendre et 30 pour le test. Les scores ci-dessous sont dans l’ordre Accuracy, Precision, Recall, F1 (moyennes pondérées pour les trois derniers).

- **RF v1.0**, 100 arbres, profondeur 5 : 93.33 %, 93.33 %, 93.33 %, 93.33 %.
- **RF v2.0**, 200 arbres, profondeur 8 : 90 %, 90.24 %, 90 %, 89.97 %.
- **KNN**, 5 voisins, données standardisées : 93.33 %, 94.44 %, 93.33 %, 93.27 %.

Le Random Forest plus grand n’a pas mieux réussi sur ce test.

Captures MLflow : [les runs](reports/mlflow-experiments.png) et [les détails du Random Forest](reports/mlflow-random-forest.png).

## Restaurer une version

Le dépôt contient les branches `main` et `develop`, plusieurs commits et deux tags.

```powershell
git switch --detach v1.0
dvc checkout
# Si le cache est vide et que le remote est accessible :
dvc pull
```

Le stockage DVC est le dossier local `dvc-storage`, absent de GitHub. Sur une autre machine, il faut le transférer et configurer son chemin, ou régénérer les données avec les commandes ci-dessus.

La restauration de Wine et le réentraînement ont été vérifiés dans un clone séparé : [résultat](reports/reproduction.json). Le pipeline a aussi [réussi sur Ubuntu avec GitHub Actions](https://github.com/Masoudi00/tp/actions/runs/42068352711).

## Réponses aux questions

1. **Git et DVC ?** Git suit le code et les configurations ; DVC suit les données et les modèles.
2. **Pourquoi pas les gros datasets dans Git ?** Ils alourdissent l’historique et les clonages.
3. **`dvc add` et `dvc repro` ?** Le premier versionne un fichier ; le second relance les étapes du pipeline qui ont changé.
4. **`dvc.lock` ?** Il garde les paramètres et les empreintes des fichiers du pipeline.
5. **Comparer avec MLflow ?** Sélectionner les runs pour comparer leurs paramètres et leurs métriques.
6. **Retrouver les fichiers d’un commit ?** Faire `git checkout`, puis `dvc checkout` ou `dvc pull` si le cache est vide.
7. **Pourquoi la reproductibilité ?** Pour refaire une expérience et vérifier son résultat.
8. **Modèles dans DVC ou MLflow ?** DVC conserve les versions des fichiers ; MLflow conserve les expériences, leurs scores et leurs artefacts.
