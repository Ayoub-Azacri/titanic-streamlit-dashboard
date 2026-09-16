import plotly.graph_objects as go
from PIL import Image, ImageDraw

def hex_to_rgb(h):
    h = h.lstrip('#')
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

def draw_person(d, cx, cy_head, r_head, w_body, h_body, r_body, color, has_slit=True, cutout=0):
    """Trace un personnage avec pochoir de découpe et fente pour un rendu multi-figures net."""
    if cutout > 0:
        d.ellipse([cx - (r_head + cutout), cy_head - (r_head + cutout),
                   cx + (r_head + cutout), cy_head + (r_head + cutout)], fill=(0, 0, 0, 0))
        d.rounded_rectangle([cx - (w_body / 2 + cutout), cy_head + r_head + 26 - cutout,
                             cx + (w_body / 2 + cutout), cy_head + r_head + 26 + h_body + cutout],
                            radius=int(r_body + cutout), fill=(0, 0, 0, 0))

    d.ellipse([cx - r_head, cy_head - r_head, cx + r_head, cy_head + r_head], fill=color)
    d.rounded_rectangle([cx - w_body / 2, cy_head + r_head + 26,
                         cx + w_body / 2, cy_head + r_head + 26 + h_body],
                        radius=int(r_body), fill=color)
    if has_slit:
        slit_w, slit_h = 20, 160
        y_bottom = cy_head + r_head + 26 + h_body
        d.rectangle([cx - slit_w / 2, y_bottom - slit_h, cx + slit_w / 2, y_bottom + 10], fill=(0, 0, 0, 0))

def make_silhouette(kind, color_hex, size=80):
    """Génère les silhouettes vectorielles officielles haute fidélité (Notebook TP3)."""
    s = 720
    color = hex_to_rgb(color_hex)
    im = Image.new('RGBA', (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    cx = s // 2

    if kind == 'woman':
        d.ellipse([cx - 64, 48, cx + 64, 176], fill=color)
        d.rounded_rectangle([cx - 86, 202, cx + 86, 296], radius=34, fill=color)
        d.polygon([(cx - 70, 270), (cx + 70, 270), (cx + 128, 574), (cx - 128, 574)], fill=color)
        d.rounded_rectangle([cx - 128, 544, cx + 128, 608], radius=28, fill=color)
    elif kind == 'man':
        d.ellipse([cx - 64, 48, cx + 64, 176], fill=color)
        d.rounded_rectangle([cx - 96, 202, cx + 96, 608], radius=38, fill=color)
        d.rectangle([cx - 14, 456, cx + 14, 615], fill=(0, 0, 0, 0))
    elif kind == 'child':
        d.ellipse([cx - 58, 172, cx + 58, 288], fill=color)
        d.rounded_rectangle([cx - 74, 310, cx + 74, 608], radius=32, fill=color)
        d.rectangle([cx - 12, 476, cx + 12, 615], fill=(0, 0, 0, 0))
    elif kind == 'solo':
        d.ellipse([cx - 64, 48, cx + 64, 176], fill=color)
        d.rounded_rectangle([cx - 90, 202, cx + 90, 608], radius=36, fill=color)
    elif kind in ('duo', 'family_3'):
        # 3 silhouettes : 2 adultes en retrait, 1 enfant au centre avec découpe pochoir
        draw_person(d, cx - 95, cy_head=100, r_head=54, w_body=140, h_body=380, r_body=32, color=color, has_slit=True)
        draw_person(d, cx + 95, cy_head=100, r_head=54, w_body=140, h_body=380, r_body=32, color=color, has_slit=True)
        draw_person(d, cx, cy_head=210, r_head=46, w_body=120, h_body=290, r_body=26, color=color, has_slit=True, cutout=16)
    elif kind in ('group', 'family_5'):
        # 5 silhouettes : 2 adultes en retrait, 3 enfants au premier plan avec découpe pochoir
        draw_person(d, cx - 110, cy_head=100, r_head=52, w_body=136, h_body=380, r_body=32, color=color, has_slit=True)
        draw_person(d, cx + 110, cy_head=100, r_head=52, w_body=136, h_body=380, r_body=32, color=color, has_slit=True)
        draw_person(d, cx - 165, cy_head=220, r_head=42, w_body=108, h_body=280, r_body=24, color=color, has_slit=True, cutout=16)
        draw_person(d, cx + 165, cy_head=220, r_head=42, w_body=108, h_body=280, r_body=24, color=color, has_slit=True, cutout=16)
        draw_person(d, cx, cy_head=200, r_head=46, w_body=118, h_body=300, r_body=26, color=color, has_slit=True, cutout=16)

    return im.resize((size, size), Image.Resampling.LANCZOS)

EMOJI_MAP = {'woman': '👩', 'child': '🧒', 'man': '👨', 'solo': '👤', 'duo': '👨‍👩‍👧', 'group': '👨‍👩‍👧‍👦'}

def fmt_pct(val, decimals=1):
    """Formatage standardisé des pourcentages avec virgule décimale (norme française)."""
    return f"{val:.{decimals}f}".replace('.', ',') + " %"

def create_gauge_chart(categories, rates, counts, dead_counts, colors, height=260, term_female=False, icon_kinds=None, icon_style="silhouettes", theme="light"):
    """
    Jauge horizontale 100 % interactive conforme au pixel près aux 4 rendus officiels du TP3.
    Prend en charge les 3 modes d'affichage d'icônes et les thèmes Clair / Sombre.
    """
    mort_rates = [round(max(0.0, 100.0 - r), 1) for r in rates]
    totals = [s + d for s, d in zip(counts, dead_counts)]
    surv_label = "survivantes" if term_female else "survivants"
    dead_label = "disparues" if term_female else "disparus"

    is_dark = (theme == "dark")
    track_bg = '#1E293B' if is_dark else '#F1F5F9'
    track_border = '#334155' if is_dark else '#CBD5E1'
    tick_color = '#E2E8F0' if is_dark else '#1E293B'
    anno_dead_color = '#94A3B8' if is_dark else '#475569'
    anno_dark_surv = '#E2E8F0' if is_dark else '#1E293B'

    # Gestion de l'étiquetage selon le style d'icône
    display_cats = categories
    if icon_style == "emojis" and icon_kinds:
        display_cats = [f"{EMOJI_MAP.get(k, '')} {cat}" for k, cat in zip(icon_kinds, categories)]

    fig = go.Figure()

    # 1. Rail de fond 100 %
    fig.add_trace(go.Bar(
        y=display_cats,
        x=[100] * len(display_cats),
        orientation='h',
        name='Capacité totale',
        marker=dict(color=track_bg, line=dict(color=track_border, width=1.3)),
        hoverinfo='none',
        showlegend=False
    ))

    # 2. Barre pleine colorée
    fig.add_trace(go.Bar(
        y=display_cats,
        x=rates,
        orientation='h',
        name='Survie',
        marker=dict(color=colors),
        showlegend=False,
        customdata=list(zip(counts, totals, dead_counts, mort_rates)),
        hovertemplate="<b>%{y}</b><br>Survie : <b>%{x:.1f} %</b> (%{customdata[0]} / %{customdata[1]})<br>Mortalité : %{customdata[3]:.1f} % (%{customdata[2]} disparus)<extra></extra>"
    ))

    # 3. Silhouettes vectorielles monochromes (si mode 'silhouettes')
    x_min = 0
    if icon_style == "silhouettes" and icon_kinds:
        x_min = -8
        for cat, c_hex, kind in zip(display_cats, colors, icon_kinds):
            ico = make_silhouette(kind, c_hex)
            fig.add_layout_image(
                dict(
                    source=ico,
                    xref='x', yref='y',
                    x=-4.5, y=cat,
                    sizex=5.5, sizey=0.75,
                    sizing='contain',
                    xanchor='center', yanchor='middle'
                )
            )

    # 4. Annotations textuelles anti-collision
    for cat, r, s_cnt, d_cnt, m in zip(display_cats, rates, counts, dead_counts, mort_rates):
        r_str = fmt_pct(r)
        m_str = fmt_pct(m)
        s_suf = "survivantes" if ("Femme" in cat or term_female) else "survivants"
        d_suf = "disparues" if ("Femme" in cat or term_female) else "disparus"

        if r >= 35:
            fig.add_annotation(
                x=r - 1.8, y=cat,
                text=f"<b>{r_str}</b> ({s_cnt} {s_suf})",
                showarrow=False,
                xanchor='right',
                yanchor='middle',
                font=dict(color='white', size=11, family='Inter, -apple-system, sans-serif')
            )
        else:
            fig.add_annotation(
                x=r + 1.8, y=cat,
                text=f"<b>{r_str}</b> ({s_cnt} {s_suf})",
                showarrow=False,
                xanchor='left',
                yanchor='middle',
                font=dict(color=anno_dark_surv, size=11, family='Inter, -apple-system, sans-serif')
            )

        if r <= 82:
            fig.add_annotation(
                x=98.5, y=cat,
                text=f"{m_str} {d_suf} ({d_cnt})",
                showarrow=False,
                xanchor='right',
                yanchor='middle',
                font=dict(color=anno_dead_color, size=10.5, family='Inter, -apple-system, sans-serif')
            )
        elif r < 99:
            fig.add_annotation(
                x=99.0, y=cat,
                text=f"{m_str} ({d_cnt})",
                showarrow=False,
                xanchor='right',
                yanchor='middle',
                font=dict(color=anno_dead_color, size=10, family='Inter, -apple-system, sans-serif')
            )

    fig.update_layout(
        barmode='overlay',
        bargap=0.36,
        margin=dict(l=10, r=14, t=8, b=8),
        height=height,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        hoverlabel=dict(bgcolor='#0F172A', font_size=12, font_family='Inter, sans-serif', font_color='#FFFFFF', bordercolor='#334155'),
        xaxis=dict(range=[x_min, 100], showgrid=False, showticklabels=False, zeroline=False),
        yaxis=dict(autorange="reversed", showgrid=False, tickfont=dict(size=12, color=tick_color, family='Inter, sans-serif')),
        showlegend=False
    )
    return fig

def create_act4_individual_chart(classes, mort_rates, dead_counts, surv_counts, totals, theme="light"):
    """
    Acte 4 - Graphique 1 : Risque individuel de décès par classe (Jauge 100 %).
    Palette : 1re & 2e en Ardoise, 3e en Cramoisi Alerte.
    """
    is_dark = (theme == "dark")
    track_bg = '#1E293B' if is_dark else '#F1F5F9'
    track_border = '#334155' if is_dark else '#CBD5E1'
    tick_color = '#E2E8F0' if is_dark else '#1E293B'
    anno_rail_color = '#94A3B8' if is_dark else '#475569'
    bar_colors = ['#64748B' if is_dark else '#475569', '#64748B' if is_dark else '#475569', '#E11D48' if is_dark else '#BE123C']
    surv_rates = [round(max(0.0, 100.0 - m), 1) for m in mort_rates]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        y=classes,
        x=[100] * len(classes),
        orientation='h',
        marker=dict(color=track_bg, line=dict(color=track_border, width=1.3)),
        hoverinfo='none',
        showlegend=False
    ))
    fig.add_trace(go.Bar(
        y=classes,
        x=mort_rates,
        orientation='h',
        name='Mortalité',
        marker=dict(color=bar_colors),
        showlegend=False,
        customdata=list(zip(dead_counts, totals, surv_counts, surv_rates)),
        hovertemplate="<b>%{y}</b><br>Mortalité individuelle : <b>%{x:.1f} %</b><br>Disparus : %{customdata[0]} / %{customdata[1]} passagers<br>Rescapés : %{customdata[2]} (%{customdata[3]:.1f} %)<extra></extra>"
    ))

    for c, m, d, cnt in zip(classes, mort_rates, dead_counts, totals):
        m_str = fmt_pct(m)
        surv_str = fmt_pct(100 - m)
        fig.add_annotation(
            x=m / 2, y=c,
            text=f"<b>{m_str}</b> ({d} / {cnt})",
            showarrow=False,
            xanchor='center',
            yanchor='middle',
            font=dict(color='white', size=11, family='Inter, sans-serif')
        )
        fig.add_annotation(
            x=98.5, y=c,
            text=f"{surv_str} sauvés",
            showarrow=False,
            xanchor='right',
            yanchor='middle',
            font=dict(color=anno_rail_color, size=10.5, family='Inter, sans-serif')
        )

    fig.update_layout(
        barmode='overlay',
        bargap=0.36,
        margin=dict(l=10, r=14, t=8, b=8),
        height=240,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        hoverlabel=dict(bgcolor='#0F172A', font_size=12, font_family='Inter, sans-serif', font_color='#FFFFFF', bordercolor='#334155'),
        xaxis=dict(range=[0, 100], showgrid=False, showticklabels=False, zeroline=False),
        yaxis=dict(autorange="reversed", showgrid=False, tickfont=dict(size=12, color=tick_color, family='Inter, sans-serif')),
        showlegend=False
    )
    return fig

def create_act4_losses_chart(classes, loss_shares, dead_counts, total_deaths=549, theme="light"):
    """
    Acte 4 - Graphique 2 : Répartition absolue des 549 disparus sur jauge 100 %.
    Palette : 1re & 2e en Ardoise, 3e en Cramoisi Alerte.
    """
    is_dark = (theme == "dark")
    track_bg = '#1E293B' if is_dark else '#F1F5F9'
    track_border = '#334155' if is_dark else '#CBD5E1'
    tick_color = '#E2E8F0' if is_dark else '#1E293B'
    anno_dark_color = '#E2E8F0' if is_dark else '#1E293B'
    bar_colors = ['#64748B' if is_dark else '#475569', '#64748B' if is_dark else '#475569', '#E11D48' if is_dark else '#BE123C']

    fig = go.Figure()
    fig.add_trace(go.Bar(
        y=classes,
        x=[100] * len(classes),
        orientation='h',
        marker=dict(color=track_bg, line=dict(color=track_border, width=1.3)),
        hoverinfo='none',
        showlegend=False
    ))
    fig.add_trace(go.Bar(
        y=classes,
        x=loss_shares,
        orientation='h',
        name='Part des pertes',
        marker=dict(color=bar_colors),
        showlegend=False,
        customdata=list(zip(dead_counts, [total_deaths]*len(classes))),
        hovertemplate="<b>%{y}</b><br>Part dans les 549 disparus : <b>%{x:.1f} %</b><br>Disparus : %{customdata[0]} / %{customdata[1]} victimes totales<extra></extra>"
    ))

    for c, s, d in zip(classes, loss_shares, dead_counts):
        s_str = fmt_pct(s)
        if s > 25:
            fig.add_annotation(
                x=s / 2, y=c,
                text=f"<b>{s_str}</b> ({d} disparus)",
                showarrow=False,
                xanchor='center',
                yanchor='middle',
                font=dict(color='white', size=11, family='Inter, sans-serif')
            )
        else:
            fig.add_annotation(
                x=s + 2.0, y=c,
                text=f"<b>{s_str}</b> ({d} disparus)",
                showarrow=False,
                xanchor='left',
                yanchor='middle',
                font=dict(color=anno_dark_color, size=11, family='Inter, sans-serif')
            )

    fig.update_layout(
        barmode='overlay',
        bargap=0.36,
        margin=dict(l=10, r=14, t=8, b=8),
        height=240,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        hoverlabel=dict(bgcolor='#0F172A', font_size=12, font_family='Inter, sans-serif', font_color='#FFFFFF', bordercolor='#334155'),
        xaxis=dict(range=[0, 100], showgrid=False, showticklabels=False, zeroline=False),
        yaxis=dict(autorange="reversed", showgrid=False, tickfont=dict(size=12, color=tick_color, family='Inter, sans-serif')),
        showlegend=False
    )
    return fig

def create_simulator_gauge(rate, color, theme="light"):
    """Jauge demi-cercle prédictive pour le simulateur personnel de survie."""
    is_dark = (theme == "dark")
    gauge_bg = '#1E293B' if is_dark else '#F1F5F9'
    gauge_border = '#334155' if is_dark else '#CBD5E1'
    title_color = '#CBD5E1' if is_dark else '#475569'
    steps = [
        dict(range=[0, 35], color="#4C1D24"),
        dict(range=[35, 65], color="#452B0F"),
        dict(range=[65, 100], color="#133E5C")
    ] if is_dark else [
        dict(range=[0, 35], color="#FFE4E6"),
        dict(range=[35, 65], color="#FEF3C7"),
        dict(range=[65, 100], color="#E0F2FE")
    ]

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=rate,
        domain=dict(x=[0.05, 0.95], y=[0.05, 0.95]),
        number=dict(suffix=" %", font=dict(size=30, color=color, family='Inter, -apple-system, sans-serif')),
        title=dict(text="Chances de survie estimées", font=dict(size=13, color=title_color, family='Inter, sans-serif')),
        gauge=dict(
            axis=dict(range=[0, 100], tickwidth=1, tickcolor="#94A3B8"),
            bar=dict(color=color),
            bgcolor=gauge_bg,
            borderwidth=1,
            bordercolor=gauge_border,
            steps=steps
        )
    ))
    fig.update_layout(
        height=240,
        margin=dict(l=20, r=20, t=32, b=16),
        paper_bgcolor='rgba(0,0,0,0)'
    )
    return fig

def render_takeaway_html(title, desc, bg, border, text_color, theme="light"):
    """Génère le code HTML d'une boîte de synthèse conforme aux 4 rendus du notebook."""
    if theme == "dark":
        if bg == "#EFF6FF":
            bg, border, text_color = "#172554", "#1E40AF", "#BFDBFE"
        elif bg == "#FFF7ED":
            bg, border, text_color = "#451A03", "#92400E", "#FDE68A"
        elif bg == "#FEF2F2":
            bg, border, text_color = "#4C0519", "#9F1239", "#FECDD3"
        elif bg == "#F8FAFC":
            bg, border, text_color = "#1E293B", "#334155", "#E2E8F0"
        else:
            bg, border, text_color = "#1E293B", "#334155", "#E2E8F0"

    return f"""<div style="background:{bg}; border:1px solid {border}; border-radius:8px; padding:10px 14px; color:{text_color}; font-size:0.85rem; line-height:1.45; margin-top:8px;">
        <strong style="display:block; margin-bottom:2px; font-weight:700;">{title}</strong>
        {desc}
    </div>"""

def get_app_css(theme="light"):
    """Design System CSS moderne avec support bi-mode Clair et Sombre."""
    is_dark = (theme == "dark")
    bg_main = "#0B1120" if is_dark else "#F8FAFC"
    bg_sidebar = "#080D1A" if is_dark else "#FFFFFF"
    border_sidebar = "#1E293B" if is_dark else "#E2E8F0"
    text_h = "#F8FAFC" if is_dark else "#0F172A"
    text_body = "#CBD5E1" if is_dark else "#1E293B"
    text_caption = "#94A3B8" if is_dark else "#64748B"
    card_bg = "#131D31" if is_dark else "#FFFFFF"
    card_border = "#1E293B" if is_dark else "#E2E8F0"
    card_border_hover = "#334155" if is_dark else "#CBD5E1"
    minto_bg = "#064E3B" if is_dark else "#F0FDF4"
    minto_border = "#047857" if is_dark else "#BBF7D0"
    minto_bar = "#10B981" if is_dark else "#16A34A"
    minto_text = "#D1FAE5" if is_dark else "#166534"
    tab_color = "#94A3B8" if is_dark else "#64748B"
    tab_active = "#38BDF8" if is_dark else "#2563EB"
    input_bg = "#131D31" if is_dark else "#FFFFFF"
    input_border = "#334155" if is_dark else "#CBD5E1"

    return f"""<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    html, body, [class*="css"], .stApp {{ font-family: 'Inter', sans-serif; background-color: {bg_main} !important; color: {text_body} !important; }}
    h1, h2, h3, h4, h5, h6, [data-testid="stHeader"] {{ color: {text_h} !important; }}
    div[data-testid="stMarkdownContainer"] p, div[data-testid="stMarkdownContainer"] span, label {{ color: {text_body} !important; }}
    [data-testid="stCaptionContainer"] p, .stCaption {{ color: {text_caption} !important; }}
    .main .block-container {{ padding-top: 1.2rem; padding-bottom: 2.2rem; max-width: 1400px; }}
    [data-testid="stSidebar"] {{ min-width: 320px; background-color: {bg_sidebar} !important; border-right: 1px solid {border_sidebar} !important; }}
    [data-testid="stSidebar"] div[data-testid="stMarkdownContainer"] p {{ color: {text_body} !important; }}
    div[data-baseweb="select"] {{ max-height: none !important; height: auto !important; }}
    div[data-baseweb="select"] > div {{ max-height: none !important; height: auto !important; flex-wrap: wrap !important; padding: 3px 5px !important; background-color: {input_bg} !important; border-color: {input_border} !important; }}
    div[data-baseweb="tag"], span[data-baseweb="tag"] {{ background-color: #1E3A8A !important; border: 1px solid #3B82F6 !important; border-radius: 6px !important; padding: 2px 7px !important; margin: 2px !important; }}
    div[data-baseweb="tag"] *, span[data-baseweb="tag"] * {{ color: #FFFFFF !important; fill: #FFFFFF !important; font-weight: 600 !important; font-size: 0.81rem !important; }}
    div[data-baseweb="tag"]:hover, span[data-baseweb="tag"]:hover {{ background-color: #2563EB !important; }}
    div[data-testid="stMetric"] {{ background-color: {card_bg} !important; border: 1px solid {card_border} !important; border-radius: 10px; padding: 10px 14px; box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08); transition: transform 0.15s ease; }}
    div[data-testid="stMetric"]:hover {{ transform: translateY(-2px); border-color: {card_border_hover}; }}
    div[data-testid="stMetricLabel"] {{ font-size: 0.74rem !important; font-weight: 600 !important; color: {text_caption} !important; text-transform: uppercase; letter-spacing: 0.04em; }}
    div[data-testid="stMetricValue"] {{ font-size: 1.55rem !important; font-weight: 700 !important; color: {text_h} !important; letter-spacing: -0.02em; }}
    div.hero-banner {{ background: linear-gradient(135deg, #020617 0%, #0F172A 100%) !important; border: 1px solid #1E293B !important; border-radius: 12px !important; padding: 22px 26px !important; margin-bottom: 18px !important; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.25) !important; }}
    div[data-testid="stMarkdownContainer"] div.hero-banner, div[data-testid="stMarkdownContainer"] div.hero-banner * {{ color: #FFFFFF !important; }}
    div[data-testid="stMarkdownContainer"] div.hero-banner h1, div[data-testid="stMarkdownContainer"] div.hero-banner .hero-title {{ font-size: 1.65rem !important; font-weight: 700 !important; margin: 0 !important; color: #FFFFFF !important; text-shadow: 0 1px 2px rgba(0, 0, 0, 0.4) !important; }}
    div[data-testid="stMarkdownContainer"] div.hero-banner p, div[data-testid="stMarkdownContainer"] div.hero-banner .hero-subtitle {{ font-size: 0.88rem !important; color: #CBD5E1 !important; margin-top: 4px !important; margin-bottom: 0 !important; }}
    div[data-testid="stMarkdownContainer"] div.hero-banner .hero-badge {{ display: inline-block !important; background: rgba(255, 255, 255, 0.12) !important; border: 1px solid rgba(255, 255, 255, 0.25) !important; border-radius: 9999px !important; padding: 3px 10px !important; font-size: 0.72rem !important; font-weight: 600 !important; color: #93C5FD !important; margin-bottom: 6px !important; }}
    div[data-testid="stMarkdownContainer"] div.hero-banner .hero-credits {{ font-size: 0.76rem !important; color: #94A3B8 !important; margin-top: 10px !important; border-top: 1px solid rgba(255, 255, 255, 0.15) !important; padding-top: 8px !important; }}
    .minto-card {{ background-color: {minto_bg} !important; border: 1px solid {minto_border} !important; border-left: 4px solid {minto_bar} !important; border-radius: 8px; padding: 11px 15px; margin-bottom: 12px; color: {minto_text} !important; font-size: 0.90rem; line-height: 1.45; }}
    .minto-card * {{ color: {minto_text} !important; }}
    div[data-testid="stTabs"] button {{ color: {tab_color} !important; }}
    div[data-testid="stTabs"] button[aria-selected="true"] {{ color: {tab_active} !important; border-bottom-color: {tab_active} !important; }}
    div[data-testid="stExpander"] {{ background-color: {card_bg} !important; border-color: {card_border} !important; }}
    </style>"""
