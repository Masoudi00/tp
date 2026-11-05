# Atelier Git DVC MLflow

Projet de classification Iris réalisé avec Git, DVC et MLflow. Deux modèles sont entraînés sur le même découpage stratifié : Random Forest et KNN avec standardisation ajustée uniquement sur les données d’entraînement. Le dataset Wine sert au deuxième exercice de versioning des données.

## Installation et exécution

Python 3.12 est utilisé pour cette réalisation. Depuis la racine du projet, sous PowerShell :

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.lock.txt
$env:DVC_SITE_CACHE_DIR="$PWD\.dvc\site-cache"
python src/prepare_data.py
python scripts/verify_data.py
dvc repro --force
python scripts/validate.py
mlflow ui --backend-store-uri sqlite:///mlflow.db --host 127.0.0.1
```

Ouvrir http://127.0.0.1:5000 puis l’expérience `TP_Iris_Classification`. Comparer les paramètres et les quatre métriques des runs. Les modèles et params.yaml sont disponibles dans les artefacts. Les tags MLflow enregistrent le commit, l’empreinte du dataset et celle des paramètres.

Sous Linux, activer avec `source .venv/bin/activate`. La variable DVC_SITE_CACHE_DIR n’est nécessaire que si le cache partagé du système n’est pas accessible.

`requirements.lock.txt` fixe les versions de l’environnement exécuté. `requirements.txt` énumère les dépendances directes. La CI Linux constitue une vérification supplémentaire, distincte de la démonstration locale.

## Résultats des expériences

Le test comprend 30 observations, avec random_state 42 et test_size 0.2. Les métriques Precision, Recall et F1 utilisent la moyenne pondérée.

- Version v1.0, Random Forest 100 arbres et profondeur 5 : Accuracy 0.933333, Precision 0.933333, Recall 0.933333, F1 0.933333.
- Version v2.0, Random Forest 200 arbres et profondeur 8 : Accuracy 0.900000, Precision 0.902357, Recall 0.900000, F1 0.899749.
- KNN, 5 voisins et poids uniformes, dans les deux versions : Accuracy 0.933333, Precision 0.944444, Recall 0.933333, F1 0.932660.

Augmenter le nombre d’arbres et la profondeur n’a pas amélioré ce test. Le changement porte sur deux hyperparamètres, donc il ne permet pas d’isoler leur effet individuel. Un seul petit jeu de test ne permet pas de conclure à une supériorité générale ; une validation croisée serait nécessaire pour choisir le modèle avec davantage de confiance.

Les valeurs complètes sont conservées dans reports/baseline.json et reports/metrics.json. La base SQLite et les artefacts MLflow restent locaux et ne sont pas stockés dans Git.

## Restaurer et reproduire

```powershell
git switch --detach v1.0
dvc checkout
# Si les objets ne sont pas dans le cache :
dvc pull
dvc repro --force --no-run-cache
git switch main
dvc checkout
```

Le remote de démonstration est `dvc-storage` à la racine du projet, ignoré par Git. `dvc push` y stocke les données et modèles. Après un clonage sur une autre machine, transférer ce stockage puis configurer `dvc remote modify --local storage url CHEMIN_ABSOLU` avant `dvc pull`. Pour une équipe, utiliser un stockage partagé et configurer ses accès séparément.

Les datasets publics intégrés à scikit-learn permettent aussi une reproduction sans transfert du remote : exécuter prepare_data.py, vérifier les empreintes, puis forcer le pipeline. Cela recalcule les modèles au lieu de les télécharger.

`python scripts/demonstrate.py` crée un clone isolé sans cache partagé, récupère v1.0 depuis le remote DVC, modifie Wine, versionne cette modification, restaure son manifeste et ses données, puis force un nouvel entraînement. Les assertions et les empreintes sont enregistrées dans reports/reproduction.json. Cette démonstration utilise la même machine et le même environnement Python ; elle ne prétend pas être un test sur une seconde machine.

## Réponses aux questions

1. Git versionne le code et les configurations. DVC versionne le contenu des données et modèles via un cache et des références légères suivies par Git.
2. Un gros dataset dans Git augmente durablement l’historique et rend clonages et transferts coûteux. DVC sépare ce stockage de l’historique du code.
3. `dvc add` suit un fichier existant et crée son manifeste. `dvc repro` exécute les étapes du pipeline dont les dépendances ou paramètres ont changé.
4. `dvc.lock` enregistre les dépendances, paramètres résolus et empreintes des sorties pour une version du pipeline.
5. MLflow conserve un run par entraînement, avec paramètres, métriques et artefacts. Son interface permet de sélectionner plusieurs runs et comparer leurs résultats.
6. Faire un checkout du commit Git, puis `dvc checkout` pour restaurer les objets du cache ou `dvc pull` pour les télécharger depuis le remote.
7. La reproductibilité permet de vérifier les résultats, retrouver l’origine d’une régression et reconstruire une version précise du modèle.
8. DVC associe des fichiers de modèles à un état du pipeline et du dépôt. MLflow conserve le contexte des expérimentations et leurs artefacts ; ce suivi ne remplace pas le stockage versionné du pipeline.

## CI et références

La GitHub Action installe les dépendances fixées, génère les deux datasets, vérifie leurs empreintes DVC, force le pipeline, recharge les modèles et contrôle les métriques ainsi qu’un seuil d’accuracy de 0.85. Les sorties sont publiées comme artefact du job. Aucun secret cloud n’est nécessaire pour ces données publiques.

Documentation officielle : [DVC repro](https://doc.dvc.org/command-reference/repro), [DVC checkout](https://doc.dvc.org/command-reference/checkout), [MLflow tracking](https://mlflow.org/docs/latest/tracking/).
