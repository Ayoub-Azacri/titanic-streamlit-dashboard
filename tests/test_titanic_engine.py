import pytest
import pandas as pd
import numpy as np
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from titanic_engine import (
    load_titanic_data,
    get_act1_stats,
    get_act2_stats,
    get_act3_stats,
    get_act4_stats,
    filter_data,
    simulate_survival,
    get_odds_ratio,
    get_influencing_factors,
    get_matching_cohort_samples,
)

def test_load_titanic_data():
    df = load_titanic_data()
    assert len(df) == 891
    assert df['survived'].sum() == 342
    assert (1 - df['survived']).sum() == 549
    assert 'family_size' in df.columns
    assert 'family_group' in df.columns
    assert 'died' in df.columns

def test_act1_stats():
    df = load_titanic_data()
    stats = get_act1_stats(df)
    
    assert stats.loc['woman', 'Total passagers'] == 271
    assert stats.loc['woman', 'Survivants'] == 205
    assert stats.loc['woman', 'Taux de survie (%)'] == 75.6

    assert stats.loc['child', 'Total passagers'] == 83
    assert stats.loc['child', 'Survivants'] == 49
    assert stats.loc['child', 'Taux de survie (%)'] == 59.0

    assert stats.loc['man', 'Total passagers'] == 537
    assert stats.loc['man', 'Survivants'] == 88
    assert stats.loc['man', 'Taux de survie (%)'] == 16.4

def test_act2_stats():
    df = load_titanic_data()
    stats = get_act2_stats(df)
    
    assert stats.loc[('First', 'female'), 'Survivants'] == 91
    assert stats.loc[('First', 'female'), 'Total'] == 94
    assert stats.loc[('First', 'female'), 'Taux (%)'] == 96.8

    assert stats.loc[('First', 'male'), 'Survivants'] == 45
    assert stats.loc[('First', 'male'), 'Total'] == 122
    assert stats.loc[('First', 'male'), 'Taux (%)'] == 36.9

    assert stats.loc[('Third', 'female'), 'Survivants'] == 72
    assert stats.loc[('Third', 'female'), 'Total'] == 144
    assert stats.loc[('Third', 'female'), 'Taux (%)'] == 50.0

    assert stats.loc[('Third', 'male'), 'Survivants'] == 47
    assert stats.loc[('Third', 'male'), 'Total'] == 347
    assert stats.loc[('Third', 'male'), 'Taux (%)'] == 13.5

def test_act3_stats():
    df = load_titanic_data()
    stats = get_act3_stats(df)
    
    assert stats.loc['Petite famille (2 à 4 pers.)', 'Survivants'] == 169
    assert stats.loc['Petite famille (2 à 4 pers.)', 'Total'] == 292
    assert stats.loc['Petite famille (2 à 4 pers.)', 'Taux (%)'] == 57.9

    assert stats.loc['Voyageur seul (1 pers.)', 'Survivants'] == 163
    assert stats.loc['Voyageur seul (1 pers.)', 'Total'] == 537
    assert stats.loc['Voyageur seul (1 pers.)', 'Taux (%)'] == 30.4

    assert stats.loc['Grande famille (5 pers. et +)', 'Survivants'] == 10
    assert stats.loc['Grande famille (5 pers. et +)', 'Total'] == 62
    assert stats.loc['Grande famille (5 pers. et +)', 'Taux (%)'] == 16.1

def test_act4_stats():
    df = load_titanic_data()
    stats = get_act4_stats(df)
    
    assert stats.loc['Third', 'Disparus'] == 372
    assert stats.loc['Third', 'Total passagers'] == 491
    assert stats.loc['Third', 'Taux mortalité (%)'] == 75.8
    assert stats.loc['Third', 'Part des pertes totales (%)'] == 67.8

def test_filter_data_standard():
    df = load_titanic_data()
    filtered, summary = filter_data(df, classes=['First'], sexes=['female'])
    assert summary['total'] == 94
    assert summary['survived'] == 91
    assert summary['survival_rate'] == 96.8

def test_filter_data_empty_selection():
    df = load_titanic_data()
    filtered, summary = filter_data(df, classes=[])
    assert summary['total'] == 0
    assert summary['survived'] == 0
    assert summary['survival_rate'] == 0.0

def test_simulate_survival():
    res_1 = simulate_survival(pclass='First', sex='female', age=25, family_size=3)
    assert res_1['rate'] > 90.0
    assert 'historique' in res_1

    res_3 = simulate_survival(pclass='Third', sex='male', age=30, family_size=1)
    assert res_3['rate'] < 20.0

    res_baby = simulate_survival(pclass='Second', sex='male', age=1, family_size=3)
    assert res_baby['rate'] > 80.0

def test_get_odds_ratio():
    # 76.8% vs 38.4% -> ~2.0x
    ratio = get_odds_ratio(76.8)
    assert 1.95 <= ratio <= 2.05
    # 0% -> 0.0x
    assert get_odds_ratio(0.0) == 0.0

def test_get_influencing_factors():
    factors = get_influencing_factors(pclass='First', sex='female', age=25, family_size=3)
    assert len(factors) == 4
    # Gender factor should be positive for female
    gender_f = next(f for f in factors if f['facteur'] == 'Genre')
    assert gender_f['impact'] > 0
    # Class factor should be positive for First class
    class_f = next(f for f in factors if f['facteur'] == 'Classe')
    assert class_f['impact'] > 0

def test_get_matching_cohort_samples():
    df = load_titanic_data()
    samples = get_matching_cohort_samples(df, pclass='First', sex='female', limit=3)
    assert len(samples) <= 3
    assert all(samples['class'] == 'First')
    assert all(samples['sex'] == 'female')

    # Test age-proximity sorting
    samples_child = get_matching_cohort_samples(df, pclass='First', sex='male', age=5, limit=2)
    assert len(samples_child) > 0
    assert samples_child['age'].iloc[0] <= 15

def test_simulate_survival_age_sensitivity():
    # 3rd class male child vs adult
    res_child = simulate_survival('Third', 'male', age=5, family_size=3)
    res_adult = simulate_survival('Third', 'male', age=40, family_size=3)
    assert res_child['rate'] > res_adult['rate']

    # 1st class male child vs senior
    res_1st_child = simulate_survival('First', 'male', age=5, family_size=1)
    res_1st_senior = simulate_survival('First', 'male', age=65, family_size=1)
    assert res_1st_child['rate'] > res_1st_senior['rate']

