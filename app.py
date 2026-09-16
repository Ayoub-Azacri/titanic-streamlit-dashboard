import streamlit as st
import pandas as pd
import numpy as np
import os
from titanic_engine import (
    load_titanic_data,
    get_act1_stats,
    get_act2_stats,
    get_act3_stats,
    get_act4_stats,
    filter_data,
    simulate_survival,
    get_matching_cohort_samples,
)
from titanic_visuals import (
    create_gauge_chart,
    create_act4_individual_chart,
    create_act4_losses_chart,
    create_simulator_gauge,
    render_takeaway_html,
    get_app_css,
)

# 1. Configuration de la page
st.set_page_config(
    page_title="Titanic · Storytelling & Dashboard Décisionnel",
    page_icon="🚢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Données
df = load_titanic_data()

# 3. Sidebar interactive & Sélecteur de thème
with st.sidebar:
    st.markdown("### 🚢 Titanic Analytics")
    st.caption("Plateforme d'aide à la décision · HETIC MD4")
    st.markdown("<span style='font-size:0.75rem; color:#64748B;'>Équipe : AZACRI · EL HAJJI · HAKIK · DEKHAIL</span>", unsafe_allow_html=True)
    
    dark_mode = st.toggle("🌙 Mode Sombre", value=st.session_state.get('dark_mode', False), help="Basculer entre thème clair et sombre")
    st.session_state['dark_mode'] = dark_mode
    theme = "dark" if dark_mode else "light"
    st.markdown(get_app_css(theme), unsafe_allow_html=True)
    st.divider()

    st.markdown("**🧭 Navigation thématique**")
    nav_option = st.radio(
        "Sélectionnez une vue :",
        [
            "📜 Enquête complète",
            "1️⃣ « Les femmes et les enfants d'abord »",
            "2️⃣ Le statut social traverse le genre",
            "3️⃣ La taille du foyer détermine la survie",
            "4️⃣ Le fardeau de la 3e classe",
            "🔮 Simulateur personnel de survie",
            "📋 Registre des passagers (Données)"
        ],
        label_visibility="collapsed"
    )

    st.divider()
    st.markdown("**🔍 Filtres analytiques**")
    
    selected_classes = st.multiselect(
        "Classe de voyage :", options=['First', 'Second', 'Third'], default=['First', 'Second', 'Third'],
        format_func=lambda x: {'First': '1re classe', 'Second': '2e classe', 'Third': '3e classe'}[x]
    )
    who_map = {'woman': 'Femmes', 'child': 'Enfants (< 16 ans)', 'man': 'Hommes adultes'}
    who_opts = list(who_map.keys())
    selected_who = st.multiselect("Profil & Genre :", options=who_opts, default=who_opts, format_func=lambda x: who_map[x])
    fam_map = {'Voyageur seul (1 pers.)': 'Seul (1)', 'Petite famille (2 à 4 pers.)': 'Famille (2-4)', 'Grande famille (5 pers. et +)': 'Famille (5+)'}
    fam_opts = list(fam_map.keys())
    selected_families = st.multiselect("Structure familiale :", options=fam_opts, default=fam_opts, format_func=lambda x: fam_map[x])

    if st.button("🔄 Réinitialiser les filtres", use_container_width=True):
        st.rerun()

    st.divider()
    st.markdown("**🎨 Style d'affichage des icônes**")
    icon_map = {"Silhouettes officielles (Monochrome)": "silhouettes", "Symboles textuels (Émojis)": "emojis", "Sans icône (Épuré)": "none"}
    icon_style = icon_map[st.selectbox("Silhouettes et symboles :", options=list(icon_map.keys()), index=0)]

# 5. Filtrage dynamique
filtered_df, summary = filter_data(
    df,
    classes=selected_classes,
    who_categories=selected_who,
    family_groups=selected_families
)

# 6. Hero Banner Executive
st.markdown("""
<div class="hero-banner">
    <div class="hero-badge">Rapport officiel Seaborn · N=891 passagers</div>
    <h1 class="hero-title">Naufrage du Titanic : Storytelling & Visualisation Décisionnelle</h1>
    <p class="hero-subtitle">Enquête statistique sur les déterminants de survie lors du naufrage du 15 avril 1912.</p>
    <div class="hero-credits">
        <strong>Équipe :</strong> Ayoub AZACRI · Youssef EL HAJJI · Omar HAKIK · Youssef DEKHAIL
    </div>
</div>
""", unsafe_allow_html=True)

# KPIs globaux
g_c1, g_c2, g_c3, g_c4 = st.columns(4)
g_c1.metric("Échantillon analysé", f"{summary['total']} / 891", f"{round(summary['total']/891*100, 1)}% du total")
g_c2.metric("Survivants", f"{summary['survived']}", f"{summary['survival_rate']:.1f} % de survie")
g_c3.metric("Pertes humaines", f"{summary['died']}", f"-{summary['mortality_rate']:.1f} % décès", delta_color="inverse")
if summary['total'] == 891:
    g_c4.metric("Priorité maritime", "75,6 % vs 16,4 %", "Femmes vs Hommes")
else:
    diff = round(summary['survival_rate'] - 38.4, 1)
    g_c4.metric("Écart / Moyenne globale", f"{summary['survival_rate']:.1f} %", f"{diff:+.1f} pts vs globale")

st.markdown("<div style='height: 14px;'></div>", unsafe_allow_html=True)

if summary['total'] == 0:
    st.warning("⚠️ Aucun passager ne correspond aux critères sélectionnés dans la barre latérale.")
    st.stop()

# 7. Sections d'analyse
# --- FEMMES ET ENFANTS D'ABORD ---
if nav_option in ["📜 Enquête complète", "1️⃣ « Les femmes et les enfants d'abord »"]:
    is_flt1 = (summary['total'] < 891)
    st.subheader(f"« Les femmes et les enfants d'abord »" + (f" · Cohorte ({summary['total']} passagers)" if is_flt1 else ""))
    st.caption(f"Jauge de survie (barre pleine) et de mortalité (barre vide) selon le profil démographique ({summary['total']} passagers)")
    st.markdown("""
    <div class="minto-card">
        <strong>Message clé (Minto) :</strong> « Les femmes et les enfants d'abord » : 75,6 % des femmes et 59,0 % des enfants sauvés, contre 16,4 % des hommes adultes.
    </div>
    """, unsafe_allow_html=True)

    f_act1 = get_act1_stats(filtered_df)
    k1, k2, k3, k4 = st.columns(4)
    # Femmes
    if 'woman' in f_act1.index and f_act1.loc['woman', 'Total passagers'] > 0:
        w_r = f_act1.loc['woman', 'Taux de survie (%)']
        w_s, w_t = int(f_act1.loc['woman', 'Survivants']), int(f_act1.loc['woman', 'Total passagers'])
        k1.metric("Survie Femmes", f"{w_r:.1f} %", f"{w_s} / {w_t} rescapées" + (f" ({w_r - 75.6:+.1f} pts)" if is_flt1 else ""))
    else:
        k1.metric("Survie Femmes", "N/A", "0 passagère filtrée", delta_color="off")
    # Enfants
    if 'child' in f_act1.index and f_act1.loc['child', 'Total passagers'] > 0:
        c_r = f_act1.loc['child', 'Taux de survie (%)']
        c_s, c_t = int(f_act1.loc['child', 'Survivants']), int(f_act1.loc['child', 'Total passagers'])
        k2.metric("Survie Enfants (< 16)", f"{c_r:.1f} %", f"{c_s} / {c_t} rescapés" + (f" ({c_r - 59.0:+.1f} pts)" if is_flt1 else ""))
    else:
        k2.metric("Survie Enfants (< 16)", "N/A", "0 enfant filtré", delta_color="off")
    # Hommes
    if 'man' in f_act1.index and f_act1.loc['man', 'Total passagers'] > 0:
        m_r = f_act1.loc['man', 'Taux de survie (%)']
        m_d, m_t = int(f_act1.loc['man', 'Disparus']), int(f_act1.loc['man', 'Total passagers'])
        k3.metric("Survie Hommes adultes", f"{m_r:.1f} %", f"-{m_d} / {m_t} disparus" + (f" ({m_r - 16.4:+.1f} pts)" if is_flt1 else ""))
    else:
        k3.metric("Survie Hommes adultes", "N/A", "0 homme filtré", delta_color="off")
    # Priorité
    w_ok = ('woman' in f_act1.index and f_act1.loc['woman', 'Total passagers'] > 0)
    m_ok = ('man' in f_act1.index and f_act1.loc['man', 'Total passagers'] > 0)
    if w_ok and m_ok and f_act1.loc['man', 'Taux de survie (%)'] > 0:
        p_ratio = round(f_act1.loc['woman', 'Taux de survie (%)'] / f_act1.loc['man', 'Taux de survie (%)'], 1)
        k4.metric("Priorité maritime", f"{p_ratio}×", "Femmes vs Hommes adultes")
    elif w_ok and not m_ok:
        k4.metric("Priorité maritime", "100 %", "Femmes exclusives")
    else:
        k4.metric("Priorité maritime", "N/A", "Comparaison non dispo", delta_color="off")

    f_act1_active = f_act1[f_act1['Total passagers'] > 0]
    color_map1 = {'woman': '#1E3A8A', 'child': '#0284C7', 'man': '#475569'}
    labels_f1 = {'woman': 'Femmes', 'child': 'Enfants (< 16 ans)', 'man': 'Hommes adultes'}
    f_labels = [labels_f1.get(idx, idx) for idx in f_act1_active.index]
    f_kinds = [idx if idx in ['woman', 'child', 'man'] else 'solo' for idx in f_act1_active.index]
    f_colors = [color_map1.get(idx, '#475569') for idx in f_act1_active.index]
    h1 = 140 if len(f_act1_active) == 1 else (195 if len(f_act1_active) == 2 else 250)
    fig1_f = create_gauge_chart(
        f_labels, f_act1_active['Taux de survie (%)'].tolist(), f_act1_active['Survivants'].tolist(),
        f_act1_active['Disparus'].tolist(), f_colors,
        height=h1, icon_kinds=f_kinds, icon_style=icon_style, theme=theme
    )

    if is_flt1:
        tab1_flt, tab1_ref = st.tabs([f"🔍 Cohorte active filtrée ({summary['total']} passagers)", "📊 Référence officielle (891 passagers)"])
        with tab1_flt:
            st.plotly_chart(fig1_f, use_container_width=True)
        with tab1_ref:
            act1_df = get_act1_stats(df)
            fig1 = create_gauge_chart(
                ['Femmes', 'Enfants (< 16 ans)', 'Hommes adultes'],
                act1_df['Taux de survie (%)'].tolist(), act1_df['Survivants'].tolist(),
                act1_df['Disparus'].tolist(), ['#1E3A8A', '#0284C7', '#475569'],
                height=250, icon_kinds=['woman', 'child', 'man'], icon_style=icon_style, theme=theme
            )
            st.plotly_chart(fig1, use_container_width=True)
    else:
        st.plotly_chart(fig1_f, use_container_width=True)

    tc1, tc2 = st.columns(2)
    tc1.markdown(render_takeaway_html(
        "Femmes et enfants : 75,6 % et 59,0 % de survie",
        "Application stricte de l'évacuation prioritaire sur les canots de sauvetage.",
        "#EFF6FF", "#BFDBFE", "#1E3A8A", theme=theme
    ), unsafe_allow_html=True)
    tc2.markdown(render_takeaway_html(
        "Hommes adultes : 83,6 % de mortalité constatée",
        "Cession systématique des places dans les canots aux passagers prioritaires.",
        "#F8FAFC", "#CBD5E1", "#334155", theme=theme
    ), unsafe_allow_html=True)
    st.divider()

# --- SECTION 2 : LE STATUT SOCIAL TRAVERSE LE GENRE ---
if nav_option in ["📜 Enquête complète", "2️⃣ Le statut social traverse le genre"]:
    is_flt2 = (summary['total'] < 891)
    st.subheader(f"Le statut social traverse le genre" + (f" · Cohorte ({summary['total']} passagers)" if is_flt2 else ""))
    st.caption(f"Jauge de survie (barre pleine) et de mortalité (barre vide) croisant classe de voyage et sexe ({summary['total']} passagers)")
    st.markdown("""
    <div class="minto-card">
        <strong>Message clé (Minto) :</strong> Le statut social traverse le genre : 96,8 % des femmes et 36,9 % des hommes sauvés en 1re classe, contre 50,0 % et 13,5 % en 3e.
    </div>
    """, unsafe_allow_html=True)

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Femmes 1re classe", "96,8 %", "91 / 94 rescapées")
    k2.metric("Femmes 3e classe", "50,0 %", "-46,8 pts vs 1re classe", delta_color="inverse")
    k3.metric("Hommes 1re classe", "36,9 %", "+23,4 pts vs 3e classe")
    k4.metric("Hommes 3e classe", "13,5 %", "-86,5 % disparus (300)", delta_color="inverse")

    act2_df = get_act2_stats(df)
    labels2 = ['1re classe · Femmes', '2e classe · Femmes', '3e classe · Femmes',
               '1re classe · Hommes', '2e classe · Hommes', '3e classe · Hommes']
    colors2 = ['#1E3A8A', '#0284C7', '#D97706', '#334155', '#475569', '#64748B']
    fig2 = create_gauge_chart(labels2, act2_df['Taux (%)'].tolist(), act2_df['Survivants'].tolist(),
                              act2_df['Disparus'].tolist(), colors2, height=350,
                              icon_kinds=['woman']*3 + ['man']*3, icon_style=icon_style, theme=theme)

    f_act2 = get_act2_stats(filtered_df)
    f_act2_active = f_act2[f_act2['Total'] > 0] if is_flt2 else f_act2
    labels2_f = [f"{c} · {'Femmes' if s == 'female' else 'Hommes'}" for c, s in f_act2_active.index]
    f_kinds2 = ['woman' if s == 'female' else 'man' for _, s in f_act2_active.index]
    fig2_f = create_gauge_chart(labels2_f, f_act2_active['Taux (%)'].tolist(), f_act2_active['Survivants'].tolist(),
                                f_act2_active['Disparus'].tolist(), colors2[:len(f_act2_active)],
                                height=max(220, 52 * len(f_act2_active)), icon_kinds=f_kinds2,
                                icon_style=icon_style, theme=theme)

    if is_flt2:
        tab2_flt, tab2_ref = st.tabs([f"🔍 Cohorte active filtrée ({summary['total']} passagers)", "📊 Référence officielle (891 passagers)"])
        with tab2_flt:
            st.plotly_chart(fig2_f, use_container_width=True)
        with tab2_ref:
            st.plotly_chart(fig2, use_container_width=True)
    else:
        st.plotly_chart(fig2, use_container_width=True)

    tc1, tc2 = st.columns(2)
    tc1.markdown(render_takeaway_html(
        "Femmes : 96,8 % sauvées en 1re classe contre 50,0 % en 3e",
        "L'enclavement en cale a condamné la moitié des passagères de 3e classe.",
        "#EFF6FF", "#BFDBFE", "#1E3A8A", theme=theme
    ), unsafe_allow_html=True)
    tc2.markdown(render_takeaway_html(
        "Hommes : la 1re classe triple presque la survie (36,9 % contre 13,5 %)",
        "Mais aucun groupe d'hommes n'égale le taux des femmes de 3e classe (50,0 %).",
        "#F8FAFC", "#CBD5E1", "#1E293B", theme=theme
    ), unsafe_allow_html=True)
    st.divider()

# --- SECTION 3 : LA TAILLE DU FOYER DÉTERMINE LA SURVIE ---
if nav_option in ["📜 Enquête complète", "3️⃣ La taille du foyer détermine la survie"]:
    is_flt3 = (summary['total'] < 891)
    st.subheader(f"La taille du foyer détermine la survie" + (f" · Cohorte ({summary['total']} passagers)" if is_flt3 else ""))
    st.caption(f"Jauge de survie (barre pleine) et de mortalité (barre vide) selon la cellule familiale à bord ({summary['total']} passagers)")
    st.markdown("""
    <div class="minto-card">
        <strong>Message clé (Minto) :</strong> La taille du foyer détermine la survie : 57,9 % en petit groupe, contre 30,4 % pour les isolés et 16,1 % en grande famille.
    </div>
    """, unsafe_allow_html=True)

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Petite famille (2 à 4)", "57,9 %", "169 / 292 rescapés (Optimum)")
    k2.metric("Voyageur seul (1 pers.)", "30,4 %", "-27,5 pts vs groupe", delta_color="inverse")
    k3.metric("Grande famille (5+)", "16,1 %", "-83,9 % disparus (52)", delta_color="inverse")
    k4.metric("Gain Effet bouclier", "+27,5 pts", "Famille 2-4 vs Voyageur seul")

    act3_df = get_act3_stats(df)
    fig3 = create_gauge_chart(act3_df.index.tolist(), act3_df['Taux (%)'].tolist(), act3_df['Survivants'].tolist(),
                              act3_df['Disparus'].tolist(), ['#0F766E', '#475569', '#BE123C'], height=250,
                              icon_kinds=['duo', 'solo', 'group'], icon_style=icon_style, theme=theme)

    f_act3 = get_act3_stats(filtered_df)
    f_act3_active = f_act3[f_act3['Total'] > 0] if is_flt3 else f_act3
    g_map = {'Petite famille (2 à 4 pers.)': 'duo', 'Voyageur seul (1 pers.)': 'solo', 'Grande famille (5 pers. et +)': 'group'}
    f_kinds3 = [g_map.get(idx, 'solo') for idx in f_act3_active.index]
    fig3_f = create_gauge_chart(f_act3_active.index.tolist(), f_act3_active['Taux (%)'].tolist(),
                                f_act3_active['Survivants'].tolist(), f_act3_active['Disparus'].tolist(),
                                ['#0F766E', '#475569', '#BE123C'][:len(f_act3_active)],
                                height=max(200, 70 * len(f_act3_active)), icon_kinds=f_kinds3,
                                icon_style=icon_style, theme=theme)

    if is_flt3:
        tab3_flt, tab3_ref = st.tabs([f"🔍 Cohorte active filtrée ({summary['total']} passagers)", "📊 Référence officielle (891 passagers)"])
        with tab3_flt:
            st.plotly_chart(fig3_f, use_container_width=True)
        with tab3_ref:
            st.plotly_chart(fig3, use_container_width=True)
    else:
        st.plotly_chart(fig3, use_container_width=True)

    tc1, tc2 = st.columns(2)
    tc1.markdown(render_takeaway_html(
        "Effet bouclier : voyager de 2 à 4 portait la survie à 57,9 %",
        "Gain de +27,5 points par rapport aux passagers isolés via l'assistance mutuelle.",
        "#F0FDFA", "#99F6E4", "#0F766E", theme=theme
    ), unsafe_allow_html=True)
    tc2.markdown(render_takeaway_html(
        "Piège de la panique : 83,9 % de mortalité à 5 et +",
        "52 disparus sur 62 membres en raison du coût critique de regroupement dans le noir.",
        "#FFF1F2", "#FECDD3", "#9F1239", theme=theme
    ), unsafe_allow_html=True)
    st.divider()

# --- SECTION 4 : FARDEAU DE LA 3E CLASSE ---
if nav_option in ["📜 Enquête complète", "4️⃣ Le fardeau de la 3e classe"]:
    st.subheader("Le fardeau de la 3e classe")
    st.caption("Comparaison entre le risque individuel de décès par classe (gauche) et la part contributive aux 549 disparus du naufrage (droite)")
    st.markdown("""
    <div class="minto-card">
        <strong>Message clé (Minto) :</strong> Le fardeau de la 3e classe : 75,8 % de risque individuel et 67,8 % de toutes les victimes du naufrage.
    </div>
    """, unsafe_allow_html=True)

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Risque individuel 3e classe", "75,8 %", "372 décès sur 491 passagers", delta_color="inverse")
    k2.metric("Poids dans les 549 disparus", "67,8 %", "372 victimes sur 549", delta_color="inverse")
    k3.metric("Risque individuel 1re classe", "37,0 %", "80 décès sur 216")
    k4.metric("Sur-risque 3e classe", "× 2,0", "+38,8 pts vs 1re classe")

    act4_df = get_act4_stats(df)
    classes_labels = ['1re classe', '2e classe', '3e classe']

    col4_1, col4_2 = st.columns(2)
    with col4_1:
        st.markdown("**1. Risque individuel de décès (par classe)**")
        st.caption("75,8 % des passagers ont péri en 3e classe")
        fig4_1 = create_act4_individual_chart(
            classes=classes_labels, mort_rates=act4_df['Taux mortalité (%)'].tolist(),
            dead_counts=act4_df['Disparus'].tolist(), surv_counts=act4_df['Survivants'].tolist(),
            totals=act4_df['Total passagers'].tolist(), theme=theme
        )
        st.plotly_chart(fig4_1, use_container_width=True)

    with col4_2:
        st.markdown("**2. Répartition absolue des 549 disparus**")
        st.caption("Plus des deux tiers des victimes venaient de 3e classe")
        fig4_2 = create_act4_losses_chart(
            classes=classes_labels, loss_shares=act4_df['Part des pertes totales (%)'].tolist(),
            dead_counts=act4_df['Disparus'].tolist(), total_deaths=549, theme=theme
        )
        st.plotly_chart(fig4_2, use_container_width=True)

    tc1, tc2 = st.columns(2)
    tc1.markdown(render_takeaway_html(
        "Risque individuel maximal : 75,8 % de mortalité en 3e classe",
        "Contre 37,0 % en 1re classe et 52,7 % en 2e classe.",
        "#F8FAFC", "#CBD5E1", "#334155", theme=theme
    ), unsafe_allow_html=True)
    tc2.markdown(render_takeaway_html(
        "Hécatombe absolue : 372 disparus en 3e classe",
        "Plus des deux tiers (67,8 %) de toutes les victimes du naufrage.",
        "#FFF1F2", "#FECDD3", "#9F1239", theme=theme
    ), unsafe_allow_html=True)
    st.divider()

# --- SIMULATEUR ---
if nav_option in ["📜 Enquête complète", "🔮 Simulateur personnel de survie"]:
    st.subheader("🔮 Simulateur personnel de survie")
    st.caption("Modélisation statistique bayésienne et identification de votre cohorte miroir.")

    with st.container(border=True):
        sc1, sc2 = st.columns(2)
        sim_class = sc1.selectbox("Classe de voyage :", ['First', 'Second', 'Third'], format_func=lambda x: {'First': '1re classe', 'Second': '2e classe', 'Third': '3e classe'}[x])
        sim_sex = sc2.selectbox("Genre :", ['female', 'male'], format_func=lambda x: {'female': 'Femme', 'male': 'Homme'}[x])
        sc3, sc4 = st.columns(2)
        sim_age = sc3.slider("Âge à bord :", min_value=1, max_value=80, value=25)
        sim_fam = sc4.slider("Nombre de proches à bord :", min_value=0, max_value=8, value=1)

    total_family_size = sim_fam + 1
    res = simulate_survival(sim_class, sim_sex, sim_age, total_family_size)

    col_res_metric, col_res_gauge = st.columns([1.1, 0.9])
    with col_res_metric:
        if theme == "dark":
            b_bg = "#1E293B" if res['rate'] >= 65 else ("#2A2415" if res['rate'] >= 35 else "#31181E")
            b_brd = "#3B82F6" if res['rate'] >= 65 else ("#D97706" if res['rate'] >= 35 else "#F43F5E")
            label_col = "#94A3B8"
        else:
            b_bg = "#EFF6FF" if res['rate'] >= 65 else ("#FFFBEB" if res['rate'] >= 35 else "#FFF1F2")
            b_brd = "#BFDBFE" if res['rate'] >= 65 else ("#FDE68A" if res['rate'] >= 35 else "#FECDD3")
            label_col = "#64748B"
        st.markdown(f"""
        <div style="background:{b_bg}; border:1px solid {b_brd}; border-radius:8px; padding:8px 14px; margin-bottom:10px;">
            <div style="font-size:0.75rem; font-weight:600; text-transform:uppercase; color:{label_col};">Diagnostic prédictif</div>
            <strong style="font-size:1.08rem; color:{res['color']}; display:block; margin-top:2px;">{res['verdict']}</strong>
        </div>
        """, unsafe_allow_html=True)
        st.metric(
            "Taux de survie estimé",
            f"{res['rate']:.1f} %",
            f"{res['odds_ratio']}× la moyenne globale (38,4 %)",
            delta_color="normal" if res['rate'] >= 38.4 else "inverse"
        )
        st.write(res['desc'])
        st.caption(f"Cohorte historique réelle : {res['historique']['total_cohorte']} passagers ({res['historique']['survivants_cohorte']} survivants).")

    with col_res_gauge:
        fig_sim = create_simulator_gauge(res['rate'], res['color'], theme=theme)
        st.plotly_chart(fig_sim, use_container_width=True)

    st.markdown("**📊 Décomposition des facteurs d'influence démographique**")
    cols_f = st.columns(4)
    for idx, f in enumerate(res['factors']):
        sign = "+" if f['impact'] > 0 else ""
        delta_color = "normal" if f['impact'] > 0 else ("off" if f['impact'] == 0 else "inverse")
        cols_f[idx].metric(label=f['facteur'], value=f['detail'].split('(')[0].strip(), delta=f"{sign}{f['impact']:.1f} pts", delta_color=delta_color)

    st.markdown("**👥 Passagers historiques réels ayant ce profil**")
    samples = get_matching_cohort_samples(df, sim_class, sim_sex, age=sim_age, limit=5)
    st.dataframe(
        samples[['class', 'sex', 'age', 'fare', 'family_size', 'survived', 'embark_town']].rename(columns={
            'class': 'Classe',
            'sex': 'Genre',
            'age': 'Âge',
            'fare': 'Tarif (£)',
            'family_size': 'Taille foyer',
            'survived': 'Rescapé (1=Oui, 0=Non)',
            'embark_town': 'Port embarquement'
        }),
        use_container_width=True
    )
    st.divider()

# --- REGISTRE DES PASSAGERS ---
if nav_option == "📋 Registre des passagers (Données)":
    st.subheader("📋 Registre officiel des passagers du Titanic")
    st.caption(f"Exploration granulaire de la base Seaborn ({len(filtered_df)} passagers sélectionnés).")

    search_query = st.text_input("🔍 Rechercher par port, statut ou classe :", placeholder="ex: Southampton, Cherbourg, child...")
    
    view_df = filtered_df.copy()
    if search_query:
        mask = view_df.astype(str).apply(lambda x: x.str.contains(search_query, case=False)).any(axis=1)
        view_df = view_df[mask]

    display_cols = ['class', 'sex', 'age', 'sibsp', 'parch', 'family_size', 'family_group', 'fare', 'survived', 'who', 'embark_town']
    available_cols = [c for c in display_cols if c in view_df.columns]
    
    st.dataframe(
        view_df[available_cols].rename(columns={
            'class': 'Classe',
            'sex': 'Genre',
            'age': 'Âge',
            'sibsp': 'Frères/Époux',
            'parch': 'Parents/Enfants',
            'family_size': 'Taille foyer',
            'family_group': 'Groupe familial',
            'fare': 'Tarif (£)',
            'survived': 'Rescapé (1=Oui)',
            'who': 'Profil',
            'embark_town': 'Port embarquement'
        }),
        use_container_width=True,
        height=450
    )

    csv_data = view_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Exporter la sélection filtrée (CSV)",
        data=csv_data,
        file_name="passagers_titanic_selection.csv",
        mime="text/csv",
        use_container_width=True
    )

st.caption("Projet HETIC MD4 · Tableau de bord décisionnel Titanic · Ayoub AZACRI, Youssef EL HAJJI, Omar HAKIK, Youssef DEKHAIL")
