import pandas as pd
import numpy as np
import seaborn as sns

try:
    import streamlit as st
    cache_decorator = st.cache_data
except Exception:
    def cache_decorator(f):
        return f

GLOBAL_AVERAGE_SURVIVAL = 38.38  # 342 / 891 * 100

@cache_decorator
def load_titanic_data():
    """
    Charge le dataset officiel Seaborn Titanic (891 passagers)
    et applique le feature engineering requis pour l'analyse narrative.
    """
    df = sns.load_dataset('titanic')

    # Taille du foyer (Passager + frères/soeurs/époux + parents/enfants)
    df['family_size'] = df['sibsp'] + df['parch'] + 1

    def assign_family_group(size):
        if size == 1:
            return 'Voyageur seul (1 pers.)'
        elif 2 <= size <= 4:
            return 'Petite famille (2 à 4 pers.)'
        else:
            return 'Grande famille (5 pers. et +)'

    df['family_group'] = df['family_size'].apply(assign_family_group)

    # Indicateur de mortalité
    df['died'] = 1 - df['survived']

    # Tranches d'âge standardisées
    def assign_age_group(row):
        if pd.isna(row['age']):
            return 'Âge non renseigné'
        if row['age'] < 16:
            return 'Enfant (< 16 ans)'
        elif row['age'] <= 60:
            return 'Adulte (16-60 ans)'
        else:
            return 'Senior (60+ ans)'

    df['age_group'] = df.apply(assign_age_group, axis=1)

    return df

def get_act1_stats(df):
    """Statistiques Acte 1 : Protocole maritime (femme, enfant, homme)."""
    stats = df.groupby('who')['survived'].agg(['count', 'sum', 'mean']).reindex(['woman', 'child', 'man']).fillna(0)
    stats.columns = ['Total passagers', 'Survivants', 'Taux de survie']
    stats['Disparus'] = stats['Total passagers'] - stats['Survivants']
    stats['Taux de survie (%)'] = (stats['Taux de survie'] * 100).round(1)
    stats['Taux de mortalité (%)'] = (100 - stats['Taux de survie (%)']).round(1)
    return stats

def get_act2_stats(df):
    """Statistiques Acte 2 : Statut social croisé avec le genre."""
    order = [
        ('First', 'female'), ('Second', 'female'), ('Third', 'female'),
        ('First', 'male'), ('Second', 'male'), ('Third', 'male')
    ]
    cs_stats = df.groupby(['class', 'sex'], observed=True)['survived'].agg(['count', 'sum', 'mean']).reindex(order).fillna(0)
    cs_stats.columns = ['Total', 'Survivants', 'Taux']
    cs_stats['Disparus'] = cs_stats['Total'] - cs_stats['Survivants']
    cs_stats['Taux (%)'] = (cs_stats['Taux'] * 100).round(1)
    cs_stats['Taux mortalité (%)'] = (100 - cs_stats['Taux (%)']).round(1)
    return cs_stats

def get_act3_stats(df):
    """Statistiques Acte 3 : Taille du foyer."""
    order = ['Petite famille (2 à 4 pers.)', 'Voyageur seul (1 pers.)', 'Grande famille (5 pers. et +)']
    fam_stats = df.groupby('family_group')['survived'].agg(['count', 'sum', 'mean']).reindex(order).fillna(0)
    fam_stats.columns = ['Total', 'Survivants', 'Taux']
    fam_stats['Disparus'] = fam_stats['Total'] - fam_stats['Survivants']
    fam_stats['Taux (%)'] = (fam_stats['Taux'] * 100).round(1)
    fam_stats['Taux mortalité (%)'] = (100 - fam_stats['Taux (%)']).round(1)
    return fam_stats

def get_act4_stats(df):
    """Statistiques Acte 4 : Risque individuel vs fardeau absolu par classe."""
    order = ['First', 'Second', 'Third']
    c_counts = df.groupby('class', observed=True)['survived'].agg(['count', 'sum']).reindex(order).fillna(0)
    c_counts.columns = ['Total passagers', 'Survivants']
    c_counts['Disparus'] = c_counts['Total passagers'] - c_counts['Survivants']
    
    total_deaths = (1 - df['survived']).sum()
    if total_deaths == 0:
        total_deaths = 1
    c_counts['Taux mortalité (%)'] = np.where(c_counts['Total passagers'] > 0, (c_counts['Disparus'] / c_counts['Total passagers'] * 100).round(1), 0.0)
    c_counts['Part des pertes totales (%)'] = (c_counts['Disparus'] / total_deaths * 100).round(1)
    return c_counts

def filter_data(df, classes=None, sexes=None, who_categories=None, family_groups=None):
    """Filtre multidimensionnel dynamique avec gestion stricte des sélections vides."""
    filtered = df.copy()

    if classes is not None:
        filtered = filtered[filtered['class'].isin(classes)]
    if sexes is not None:
        filtered = filtered[filtered['sex'].isin(sexes)]
    if who_categories is not None:
        filtered = filtered[filtered['who'].isin(who_categories)]
    if family_groups is not None:
        filtered = filtered[filtered['family_group'].isin(family_groups)]

    total = len(filtered)
    survived = int(filtered['survived'].sum()) if total > 0 else 0
    died = total - survived
    rate = round((survived / total * 100), 1) if total > 0 else 0.0

    summary = {
        'total': total,
        'survived': survived,
        'died': died,
        'survival_rate': rate,
        'mortality_rate': round(100.0 - rate, 1) if total > 0 else 0.0
    }
    return filtered, summary

def get_odds_ratio(rate):
    """Calcule le multiplicateur de chance par rapport à la moyenne du navire (38.4%)."""
    if rate <= 0:
        return 0.0
    return round(rate / GLOBAL_AVERAGE_SURVIVAL, 2)

def get_influencing_factors(pclass, sex, age, family_size):
    """Calcule l'impact relatif de chaque variable sur la probabilité finale."""
    factors = []

    # 1. Facteur Genre
    if sex == 'female':
        factors.append({'facteur': 'Genre', 'detail': 'Femme (priorité canots)', 'impact': +35.8, 'type': 'positif'})
    else:
        factors.append({'facteur': 'Genre', 'detail': 'Homme adulte (cession des places)', 'impact': -22.0, 'type': 'negatif'})

    # 2. Facteur Classe sociale
    if pclass == 'First':
        factors.append({'facteur': 'Classe', 'detail': '1re classe (proximité pont supérieur)', 'impact': +24.6, 'type': 'positif'})
    elif pclass == 'Second':
        factors.append({'facteur': 'Classe', 'detail': '2e classe (accès intermédiaire)', 'impact': +8.9, 'type': 'positif'})
    else:
        factors.append({'facteur': 'Classe', 'detail': '3e classe (éloignement en cale)', 'impact': -14.2, 'type': 'negatif'})

    # 3. Facteur Âge
    if age < 16:
        factors.append({'facteur': 'Âge', 'detail': f'Enfant ({age} ans, évacuation prioritaire)', 'impact': +20.6, 'type': 'positif'})
    elif age <= 35:
        factors.append({'facteur': 'Âge', 'detail': f'Jeune adulte ({age} ans, pleine mobilité)', 'impact': +2.5, 'type': 'positif'})
    elif age <= 55:
        factors.append({'facteur': 'Âge', 'detail': f'Adulte ({age} ans, âge médian)', 'impact': -4.0, 'type': 'neutre'})
    else:
        factors.append({'facteur': 'Âge', 'detail': f'Senior ({age} ans, évacuation difficile)', 'impact': -15.0, 'type': 'negatif'})

    # 4. Facteur Taille du foyer
    if 2 <= family_size <= 4:
        factors.append({'facteur': 'Foyer', 'detail': 'Petite famille (assistance mutuelle)', 'impact': +19.5, 'type': 'positif'})
    elif family_size == 1:
        factors.append({'facteur': 'Foyer', 'detail': 'Voyageur isolé (déficit d\'alerte)', 'impact': -8.0, 'type': 'negatif'})
    else:
        factors.append({'facteur': 'Foyer', 'detail': 'Grande famille 5+ (coût de regroupement)', 'impact': -22.3, 'type': 'negatif'})

    return factors

def get_matching_cohort_samples(df, pclass, sex, age=None, limit=5):
    """Extrait un échantillon représentatif de passagers réels partageant le profil le plus proche."""
    matched = df[(df['class'] == pclass) & (df['sex'] == sex)].copy()
    if len(matched) == 0:
        matched = df[df['class'] == pclass].copy()
    if age is not None and 'age' in matched.columns:
        matched['age_diff'] = (matched['age'].fillna(30) - age).abs()
        matched = matched.sort_values('age_diff').drop(columns=['age_diff'])
    return matched.head(limit)

def simulate_survival(pclass, sex, age, family_size):
    """
    Simulateur de survie personnel basé sur un lissage Bayésien de cohorte historique
    croisant classe sociale, genre, fenêtre dynamique d'âge et structure familiale.
    """
    df = load_titanic_data()
    
    is_child = (age < 16)
    who = 'child' if is_child else ('woman' if sex == 'female' else 'man')

    if family_size == 1:
        f_group = 'Voyageur seul (1 pers.)'
        f_lift = -8.0
    elif 2 <= family_size <= 4:
        f_group = 'Petite famille (2 à 4 pers.)'
        f_lift = +19.5
    else:
        f_group = 'Grande famille (5 pers. et +)'
        f_lift = -22.3

    # 1. Base rate de la classe et du genre (échantillon N=94 à 347)
    base_sub = df[(df['class'] == pclass) & (df['sex'] == sex)]
    base_rate = (base_sub['survived'].mean() * 100.0) if len(base_sub) > 0 else GLOBAL_AVERAGE_SURVIVAL

    # 2. Fenêtre d'âge dynamique (± 8 ans) pour capturer les ruptures réelles
    age_sub = base_sub[base_sub['age'].notna()]
    w_min, w_max = max(0, age - 8), age + 8
    window_sub = age_sub[(age_sub['age'] >= w_min) & (age_sub['age'] <= w_max)]

    # 3. Calcul de survie avec prior Bayésien (évite les anomalies sur petits N)
    if is_child and pclass in ['First', 'Second']:
        child_sub = df[(df['class'] == pclass) & (df['who'] == 'child')]
        obs_rate = (child_sub['survived'].mean() * 100.0) if len(child_sub) > 0 else 100.0
        n_obs = len(child_sub)
        surv_obs = int(child_sub['survived'].sum())
        rate = obs_rate
    elif len(window_sub) > 0:
        obs_rate = window_sub['survived'].mean() * 100.0
        n_obs = len(window_sub)
        surv_obs = int(window_sub['survived'].sum())
        prior_weight = 5.0
        shrunk_rate = (prior_weight * base_rate + n_obs * obs_rate) / (prior_weight + n_obs)
        rate = shrunk_rate + (f_lift * 0.35)
    else:
        n_obs = len(base_sub)
        surv_obs = int(base_sub['survived'].sum())
        rate = base_rate + (f_lift * 0.35)

    rate = round(max(1.0, min(99.0, rate)), 1)

    if rate >= 70.0:
        verdict = "Prioritaire (Forte chance de survie)"
        color = "#1E3A8A"
        desc = "Votre profil correspondait aux personnes embarquées en priorité dans les premiers canots de sauvetage."
    elif rate >= 40.0:
        verdict = "Incertain (Survie disputée)"
        color = "#0284C7"
        desc = "Votre survie dépendait fortement de la disponibilité des canots et de l'emplacement de votre cabine."
    else:
        verdict = "Haut risque (Mortalité massive)"
        color = "#BE123C"
        desc = "Les personnes de cette catégorie ont été systématiquement sacrifiées ou bloquées dans les ponts inférieurs."

    return {
        'rate': rate,
        'mortality_rate': round(100.0 - rate, 1),
        'verdict': verdict,
        'color': color,
        'desc': desc,
        'odds_ratio': get_odds_ratio(rate),
        'factors': get_influencing_factors(pclass, sex, age, family_size),
        'historique': {
            'classe': pclass,
            'genre': 'Femme' if sex == 'female' else 'Homme',
            'profil': 'Enfant' if is_child else ('Femme adulte' if sex == 'female' else 'Homme adulte'),
            'foyer': f_group,
            'total_cohorte': n_obs,
            'survivants_cohorte': surv_obs
        }
    }
