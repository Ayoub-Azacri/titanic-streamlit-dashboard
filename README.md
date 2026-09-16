# Titanic Analytics Dashboard

Plateforme decisionnelle et recit statistique sur les determinants de survie du naufrage du Titanic (15 avril 1912).

Developpe avec Streamlit, Plotly, Pandas et Seaborn.

## Equipe du projet

* Ayoub AZACRI (Data Engineer)
* Youssef EL HAJJI (Lead Tech)
* Omar HAKIK (Data Quality)
* Youssef DEKHAIL (Data Analyst)

Promotion HETIC MD4.

## Structure analytique

Le tableau de bord presente quatre volets d'analyse chiffres, un simulateur individuel et un registre de consultation :

* « Les femmes et les enfants d'abord » : evaluation du protocole maritime d'evacuation. Le taux de survie atteint 75,6 % chez les femmes et 59,0 % chez les enfants, contre 16,4 % chez les hommes adultes.
* Le statut social traverse le genre : croisement de la classe de voyage et du sexe. La priorite accordee aux femmes s'applique a toutes les classes, mais les femmes de premiere classe atteignent 96,8 % de survie contre 50,0 % en troisieme classe.
* La taille du foyer determine la survie : impact de la cellule familiale. Les petits groupes de 2 a 4 personnes obtiennent le meilleur taux de survie (57,9 %), alors que les passagers isoles tombent a 30,4 % et les grandes familles a 16,1 %.
* Le fardeau de la troisieme classe : comparaison entre risque individuel et pertes absolues. La troisieme classe subit 75,8 % de mortalite individuelle et concentre 67,8 % de l'ensemble des victimes du naufrage.
* Simulateur personnel de survie : estimation bayesienne personnalisee basee sur la classe, le profil, l'age et la taille du foyer, completee par l'affichage d'une cohorte historique miroir.
* Registre des passagers : explorateur de donnees avec filtres multicriteres et export CSV.

## Architecture des fichiers

* `app.py` : point d'entree de l'application Streamlit, gestion des filtres dynamiques, de la navigation et des vues analytiques.
* `titanic_engine.py` : ingestion du jeu de donnees Seaborn, agregation des cohortes statistiques et moteur d'inference bayesien.
* `titanic_visuals.py` : generation des jauges Plotly a 100 %, integration des silhouettes vectorielles, styles CSS et gestion des themes clair et sombre.
* `requirements.txt` : liste des dependances Python requises pour executer l'application et les tests.
* `tests/` : suite de 17 tests unitaires et de non-regression couvrant les calculs statistiques et le rendu graphique.
* `.streamlit/config.toml` : configuration du serveur local et du theme par defaut.

## Installation et lancement

### 1. Cloner le depot

```bash
git clone https://github.com/Ayoub-Azacri/titanic-streamlit-dashboard.git
cd titanic-streamlit-dashboard
```

### 2. Creer et activer un environnement virtuel

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Installer les dependances

```bash
pip install -r requirements.txt
```

### 4. Executer les tests de verification

```bash
pytest -v
```

Les 17 tests valident l'integrite du moteur statistique et des visualisations.

### 5. Lancer l'application Streamlit

```bash
streamlit run app.py
```

L'application s'ouvre sur `http://localhost:8501`.

## Graphiques officiels de reference

Les quatre planches visuelles produites pour le livrable institutionnel sont integrees au depot :

* `AZACRI_ELHAJJI_HAKIK_DEKHAIL_1.png` : protocole maritime d'evacuation
* `AZACRI_ELHAJJI_HAKIK_DEKHAIL_2.png` : croisement classe sociale et genre
* `AZACRI_ELHAJJI_HAKIK_DEKHAIL_3.png` : effet de la taille du foyer
* `AZACRI_ELHAJJI_HAKIK_DEKHAIL_4.png` : repartition absolue des pertes par classe
