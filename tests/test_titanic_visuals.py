import pytest
import plotly.graph_objects as go
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from titanic_visuals import (
    create_gauge_chart,
    create_act4_individual_chart,
    create_act4_losses_chart,
    create_simulator_gauge,
)

def test_create_gauge_chart():
    categories = ['Femmes', 'Enfants (< 16 ans)', 'Hommes adultes']
    rates = [75.6, 59.0, 16.4]
    counts = [205, 49, 88]
    dead_counts = [66, 34, 449]
    colors = ['#1E3A8A', '#0284C7', '#475569']

    fig = create_gauge_chart(categories, rates, counts, dead_counts, colors)
    assert isinstance(fig, go.Figure)
    assert len(fig.data) == 2  # Track + Filled bar
    assert fig.layout.barmode == 'overlay'
    assert len(fig.layout.annotations) > 0

def test_create_act4_charts():
    classes = ['1re classe', '2e classe', '3e classe']
    mort_rates = [37.0, 52.7, 75.8]
    dead_counts = [80, 97, 372]
    surv_counts = [136, 87, 119]
    totals = [216, 184, 491]
    loss_shares = [14.6, 17.7, 67.8]

    fig_ind = create_act4_individual_chart(classes, mort_rates, dead_counts, surv_counts, totals)
    assert isinstance(fig_ind, go.Figure)
    assert len(fig_ind.data) == 2

    fig_loss = create_act4_losses_chart(classes, loss_shares, dead_counts, total_deaths=549)
    assert isinstance(fig_loss, go.Figure)
    assert len(fig_loss.data) == 2

def test_create_simulator_gauge():
    fig = create_simulator_gauge(75.5, '#16A34A')
    assert isinstance(fig, go.Figure)
    assert len(fig.data) == 1
    assert fig.data[0].value == 75.5

def test_create_gauge_chart_icon_styles():
    cats = ['Femmes', 'Enfants (< 16 ans)', 'Hommes adultes']
    rates = [75.6, 59.0, 16.4]
    counts = [205, 49, 88]
    dead_counts = [66, 34, 449]
    colors = ['#1E3A8A', '#0284C7', '#475569']
    kinds = ['woman', 'child', 'man']

    # 1. Silhouettes mode
    fig_sil = create_gauge_chart(cats, rates, counts, dead_counts, colors, icon_kinds=kinds, icon_style="silhouettes")
    assert len(fig_sil.layout.images) == 3
    assert fig_sil.layout.xaxis.range[0] == -8

    # 2. Emojis mode
    fig_emo = create_gauge_chart(cats, rates, counts, dead_counts, colors, icon_kinds=kinds, icon_style="emojis")
    assert len(fig_emo.layout.images) == 0
    assert '👩 Femmes' in fig_emo.data[1].y

    # 3. None mode
    fig_none = create_gauge_chart(cats, rates, counts, dead_counts, colors, icon_kinds=kinds, icon_style="none")
    assert len(fig_none.layout.images) == 0
    assert 'Femmes' in fig_none.data[1].y

def test_dark_theme_visuals():
    from titanic_visuals import render_takeaway_html, get_app_css

    cats = ['Femmes', 'Enfants', 'Hommes']
    rates, counts, dead, colors = [75.6, 59.0, 16.4], [205, 49, 88], [66, 34, 449], ['#1E3A8A', '#0284C7', '#475569']

    # 1. Gauge in dark mode
    fig_dark = create_gauge_chart(cats, rates, counts, dead, colors, theme="dark")
    assert fig_dark.data[0].marker.color == '#1E293B'
    assert fig_dark.layout.yaxis.tickfont.color == '#E2E8F0'

    # 2. Act 4 in dark mode
    fig_ind = create_act4_individual_chart(['1re', '2e', '3e'], [37.0, 52.7, 75.8], [80, 97, 372], [136, 87, 119], [216, 184, 491], theme="dark")
    assert fig_ind.data[0].marker.color == '#1E293B'
    assert fig_ind.layout.yaxis.tickfont.color == '#E2E8F0'

    # 3. Simulator in dark mode
    fig_sim = create_simulator_gauge(85.0, '#10B981', theme="dark")
    assert fig_sim.layout.paper_bgcolor == 'rgba(0,0,0,0)'

    # 4. Takeaway and CSS
    html = render_takeaway_html("Titre", "Contenu", "#EFF6FF", "#BFDBFE", "#1E3A8A", theme="dark")
    assert "background:#172554;" in html

    css = get_app_css(theme="dark")
    assert "#0B1120" in css

