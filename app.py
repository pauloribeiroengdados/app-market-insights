import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os

# ===== CONFIGURACAO =====
# Caminho do logo
LOGO_PATH = os.path.join("images", "laticinios_metropole.png")

st.set_page_config(
    page_title="Market Insights - Ação Prioritária",
    page_icon=LOGO_PATH if os.path.exists(LOGO_PATH) else "📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ===== ESTILO =====
st.markdown("""
<style>
    .metric-card {
        background: #f0f4f8;
        border-radius: 10px;
        padding: 16px 20px;
        border-left: 4px solid #2E75B6;
        margin-bottom: 8px;
    }
    .metric-card-green { border-left-color: #1E7145; background: #f0f7f0; }
    .metric-card-orange { border-left-color: #C55A11; background: #fdf3ec; }
    .metric-card-red { border-left-color: #2E75B6; background: #e8f1fb; }
    .metric-label { font-size: 13px; color: #595959; margin-bottom: 4px; }
    .metric-value { font-size: 28px; font-weight: 700; color: #1F4E79; }
    .metric-delta { font-size: 12px; color: #1E7145; }
    .section-title {
        font-size: 18px; font-weight: 600; color: #1F4E79;
        border-bottom: 2px solid #2E75B6; padding-bottom: 6px;
        margin: 20px 0 12px;
    }
    .badge-muito-alta { background:#1E7145; color:white; padding:2px 10px; border-radius:12px; font-size:12px; }
    .badge-alta       { background:#2E75B6; color:white; padding:2px 10px; border-radius:12px; font-size:12px; }
    .badge-media      { background:#C55A11; color:white; padding:2px 10px; border-radius:12px; font-size:12px; }
    .badge-baixa      { background:#595959; color:white; padding:2px 10px; border-radius:12px; font-size:12px; }
    div[data-testid="stSidebar"] { background: #f8fafc; }

    /* Botão ícone de detalhe por linha */
    button[kind="secondary"].icon-btn {
        padding: 2px 6px !important;
        min-height: 0px !important;
        height: 28px !important;
        font-size: 16px !important;
        line-height: 1 !important;
        border-radius: 6px !important;
        background: #e8f1fb !important;
        border: 1px solid #2E75B6 !important;
        color: #1F4E79 !important;
    }
    /* Linha da lista compacta */
    .lista-row {
        display: flex; align-items: center;
        padding: 4px 8px; border-bottom: 1px solid #e8e8e8;
        font-size: 13px;
    }
    .lista-row:hover { background: #f0f7fb; }
</style>
""", unsafe_allow_html=True)

# ===== COLORACAO DAS TAGS DE PRIORIDADE =====
st.markdown("""
<script>
(function() {
    const CORES = {
        "Muito Alta": "#1E7145",
        "Alta":       "#2E75B6",
        "Media":      "#C55A11",
        "Baixa":      "#595959"
    };
    function aplicarCores() {
        const tags = window.parent.document.querySelectorAll('[data-baseweb="tag"]');
        tags.forEach(function(tag) {
            const label = tag.querySelector("span");
            if (!label) return;
            const txt = label.textContent.trim();
            if (CORES[txt]) {
                tag.style.setProperty("background-color", CORES[txt], "important");
                tag.style.setProperty("border-color",     CORES[txt], "important");
                tag.querySelectorAll("span, svg").forEach(function(el) {
                    el.style.setProperty("color", "white", "important");
                    el.style.setProperty("fill",  "white", "important");
                });
            }
        });
    }
    aplicarCores();
    const obs = new MutationObserver(aplicarCores);
    obs.observe(window.parent.document.body, { childList: true, subtree: true });
})();
</script>
""", unsafe_allow_html=True)

# ===== CONSTANTES =====
UFS_TOP5  = ['MG', 'PR', 'RJ', 'RS', 'SP']
COR_PRI   = {
    'Muito Alta': '#1E7145',
    'Alta':       '#2E75B6',
    'Media':      '#C55A11',
    'Baixa':      '#9E9E9E',
}

# ===== CAMINHOS DE REFERENCIA =====
PATH_CNAE = "Public/Cnaes_Parquet/F.K03200$Z.D60214_1.CNAECSV.parquet"
PATH_MUN  = "Public/DePara_Municipios/de_para_municipios.parquet"

PORTE_DESC = {
    '00': 'Não Informado',
    '01': 'Micro Empresa',
    '03': 'Empresa de Pequeno Porte',
    '05': 'Demais',
    # aliases frequentes nos dados
    'ME':   'Micro Empresa',
    'MEI':  'Microempreendedor Individual',
    'EPP':  'Empresa de Pequeno Porte',
    'DEMAIS': 'Demais',
}

# ===== OFUSCAMENTO =====
def ofuscar_razao_social(df):
    """Substitui Razao_Social por 'Empresa XXXX' usando os últimos 4 dígitos do CNPJ."""
    if 'cnpj' in df.columns:
        df = df.copy()
        df['Razao_Social'] = df['cnpj'].astype(str).str[-4:].apply(lambda x: f'Empresa {x}')
    return df

def ofuscar_razao_social_grupo(df):
    """Substitui Razao_Social por 'Grupo XXXX' usando os 4 primeiros dígitos do CNPJ básico."""
    if 'cnpj_basico' in df.columns:
        df = df.copy()
        df['Razao_Social'] = df['cnpj_basico'].astype(str).str[:4].apply(lambda x: f'Grupo {x}')
    return df

# ===== ENRIQUECIMENTO =====
@st.cache_data
def carregar_referencias(data_path):
    """Carrega tabelas de referência de CNAE e Município."""
    refs = {}
    try:
        df_cnae = pd.read_parquet(os.path.join(data_path, PATH_CNAE))
        df_cnae['Codigo_CNAE'] = df_cnae['Codigo_CNAE'].astype(str).str.strip()
        refs['cnae'] = df_cnae.set_index('Codigo_CNAE')['Descricao_CNAE'].to_dict()
    except Exception:
        refs['cnae'] = {}
    try:
        df_mun = pd.read_parquet(os.path.join(data_path, PATH_MUN))
        # Chave: nome em maiúsculas (como está nos parquets de scoring)
        df_mun['_key'] = df_mun['codigo_municipio_rfb'].astype(str).str.strip().str.zfill(4)
        refs['municipio'] = df_mun.drop_duplicates('_key').set_index('_key')['nome_municipio'].to_dict()
    except Exception:
        refs['municipio'] = {}
    return refs

def enriquecer(df, refs):
    """Aplica descrições de CNAE, Porte e Município no DataFrame."""
    df = df.copy()
    if refs.get('cnae') and 'CNAE_Principal' in df.columns:
        # Preserva código original e cria coluna de descrição separada para tooltip
        df['CNAE_Desc'] = (
            df['CNAE_Principal'].astype(str).str.strip()
            .map(refs['cnae'])
            .fillna('Descrição não disponível')
        )
    if 'Porte' in df.columns:
        df['Porte'] = (
            df['Porte'].astype(str).str.strip().str.upper()
            .map({k.upper(): v for k, v in PORTE_DESC.items()})
            .fillna(df['Porte'])
        )
    if refs.get('municipio') and 'municipio_rfb' in df.columns:
        df['municipio_rfb'] = (
            df['municipio_rfb'].astype(str).str.strip().str.zfill(4)
            .map(refs['municipio'])
            .fillna(df['municipio_rfb'])
        )
    return df

# ===== CARREGAR DADOS =====
@st.cache_data
def carregar_dados(caminho_reat, caminho_pros):
    df_r = pd.read_parquet(caminho_reat) if os.path.exists(caminho_reat) else pd.DataFrame()
    df_p = pd.read_parquet(caminho_pros) if os.path.exists(caminho_pros) else pd.DataFrame()
    return df_r, df_p

@st.cache_data
def gerar_dados_demo():
    """Gera dados de demonstração quando os parquets reais não estão disponíveis."""
    np.random.seed(42)
    ufs   = ['SP','RJ','MG','PR','RS']
    portes= ['ME','MEI','EPP']
    pris  = ['Muito Alta','Alta','Media','Baixa']
    pesos_r = [0.037, 0.055, 0.200, 0.708]
    pesos_p = [0.009, 0.019, 0.119, 0.853]

    def base(n, pesos_pri):
        pri = np.random.choice(pris, n, p=pesos_pri)
        score = np.where(pri=='Muito Alta', np.random.uniform(0.75,1.0,n),
                np.where(pri=='Alta',       np.random.uniform(0.60,0.75,n),
                np.where(pri=='Media',      np.random.uniform(0.40,0.60,n),
                                            np.random.uniform(0.0,0.40,n))))
        uf_w = [0.43,0.08,0.14,0.10,0.25]
        return pd.DataFrame({
            'cnpj':            [f'{i:014d}' for i in range(n)],
            'Razao_Social':    [f'Empresa {i} Ltda' for i in range(n)],
            'CNAE_Principal':  np.random.choice(['4711302','4712100','4721102','4722901','4729699'], n),
            'Porte':           np.random.choice(portes, n),
            'uf_rfb':          np.random.choice(ufs, n, p=uf_w),
            'municipio_rfb':   np.random.choice(['SAO PAULO','RIO DE JANEIRO','BELO HORIZONTE','CURITIBA','PORTO ALEGRE'], n),
            'capital_social':  np.random.exponential(50000, n),
            'score_alto_valor':np.round(score, 4),
            'prioridade':      pri,
            'latitude':        np.random.uniform(-30,-20, n),
            'longitude':       np.random.uniform(-52,-43, n),
        })

    df_r = base(35256, pesos_r)
    df_p = base(344926, pesos_p)
    return df_r, df_p

# ===== SIDEBAR =====
if os.path.exists(LOGO_PATH):
    st.sidebar.image(LOGO_PATH, use_container_width=True)
else:
    st.sidebar.markdown(
        "<div style='background:#1F4E79;padding:14px;border-radius:8px;text-align:center;"
        "color:white;font-size:14px;font-weight:600;'>MBA Eng. Dados</div>",
        unsafe_allow_html=True
    )
st.sidebar.markdown("## ⚙️ Configurações")
st.sidebar.markdown("---")

# ===== FONTES DE DADOS (oculto da sidebar — configurar diretamente no código) =====
# Para conectar aos dados reais, defina os caminhos abaixo e altere usar_demo para False
usar_demo    = False
data_path    = "."
caminho_reat = os.path.join(data_path, "ml_score_reativacao_top5.parquet")
caminho_pros = os.path.join(data_path, "ml_score_prospeccao_top5.parquet")

if not usar_demo:
    df_reat, df_pros = carregar_dados(caminho_reat, caminho_pros)
    if df_reat.empty or df_pros.empty:
        df_reat, df_pros = gerar_dados_demo()
        data_path = "."
else:
    data_path = "."
    df_reat, df_pros = gerar_dados_demo()

# Ofuscamento individual aplicado nas bases carregadas
df_reat = ofuscar_razao_social(df_reat)
df_pros = ofuscar_razao_social(df_pros)

# Enriquecimento com descrições de CNAE, Porte e Município
_refs   = carregar_referencias(data_path) if not usar_demo else {'cnae': {}, 'municipio': {}}
df_reat = enriquecer(df_reat, _refs)
df_pros = enriquecer(df_pros, _refs)

st.sidebar.markdown("---")
st.sidebar.markdown("### 🔍 Filtros")

# Aba selecionada
aba = st.sidebar.radio("Visualizar", ["Reativação", "Prospecção"], horizontal=False)
df = df_reat.copy() if aba == "Reativação" else df_pros.copy()

# Filtro UF
ufs_disp = sorted(df['uf_rfb'].dropna().unique().tolist())
ufs_sel  = st.sidebar.multiselect("UF", ufs_disp, default=ufs_disp, placeholder="Selecione as opções")

# Filtro Porte
portes_disp = sorted(df['Porte'].dropna().unique().tolist())
portes_sel  = st.sidebar.multiselect("Porte", portes_disp, default=portes_disp, placeholder="Selecione as opções")

# Filtro CNAE
cnaes_disp = sorted(df['CNAE_Principal'].dropna().unique().tolist())
cnaes_sel  = st.sidebar.multiselect("CNAE Principal", cnaes_disp, default=cnaes_disp,
    placeholder="Selecione as opções",
    help="Deixe todos selecionados para não filtrar por CNAE")

# Filtro Prioridade
pris_disp = ['Muito Alta', 'Alta', 'Media', 'Baixa']
pris_sel  = st.sidebar.multiselect("Prioridade", pris_disp, default=pris_disp, placeholder="Selecione as opções")

# Filtro Score
score_min, score_max = st.sidebar.slider(
    "Faixa de Score", 0.0, 1.0, (0.0, 1.0), step=0.01
)

st.sidebar.markdown("---")
st.sidebar.markdown(
    "**Modelo:** XGBoost Exp. E  \n"
    "**F1 Macro:** 0.7585  \n"
    "**Top 5 UFs:** MG, PR, RJ, RS, SP  \n"
    "**Versão:** 2 — dados corrigidos"
)

# ===== APLICAR FILTROS =====
mask = (
    df['uf_rfb'].isin(ufs_sel) &
    df['Porte'].isin(portes_sel) &
    df['CNAE_Principal'].isin(cnaes_sel) &
    df['prioridade'].isin(pris_sel) &
    df['score_alto_valor'].between(score_min, score_max)
)
df_filtrado = df[mask].copy()

# ===== HEADER =====
icone = "🔄" if aba == "Reativação" else "🎯"
st.markdown(f"# {icone} Market Insights - Ação de {aba}")
st.markdown(
    f"**MBA Engenharia de Dados — Universidade Presbiteriana Mackenzie**  |  "
    f"Modelo XGBoost Binário + Balanceamento Geográfico  |  "
    f"Top 5 UFs: {', '.join(UFS_TOP5)}"
)
st.markdown("---")

# ===== KPIs =====
total     = len(df_filtrado)
n_ma      = (df_filtrado['prioridade'] == 'Muito Alta').sum()
n_a       = (df_filtrado['prioridade'] == 'Alta').sum()
n_alta    = n_ma + n_a
score_med = df_filtrado['score_alto_valor'].mean() if total > 0 else 0
pct_alta  = n_alta / total * 100 if total > 0 else 0

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown(f"""<div class="metric-card">
        <div class="metric-label">CNPJs filtrados</div>
        <div class="metric-value">{total:,}</div>
        <div class="metric-delta">de {len(df):,} total</div>
    </div>""", unsafe_allow_html=True)
with col2:
    st.markdown(f"""<div class="metric-card metric-card-green">
        <div class="metric-label">Muito Alta prioridade</div>
        <div class="metric-value">{n_ma:,}</div>
        <div class="metric-delta">{n_ma/total*100:.1f}% do filtrado</div>
    </div>""", unsafe_allow_html=True)
with col3:
    st.markdown(f"""<div class="metric-card">
        <div class="metric-label">Alta prioridade</div>
        <div class="metric-value">{n_a:,}</div>
        <div class="metric-delta">{n_a/total*100:.1f}% do filtrado</div>
    </div>""", unsafe_allow_html=True)
with col4:
    st.markdown(f"""<div class="metric-card metric-card-green">
        <div class="metric-label">Alta + Muito Alta</div>
        <div class="metric-value">{n_alta:,}</div>
        <div class="metric-delta">{pct_alta:.1f}% — lista priorizada</div>
    </div>""", unsafe_allow_html=True)

st.markdown("---")

# ===== GRAFICOS LINHA 1 =====
st.markdown('<div class="section-title">📊 Distribuição por Prioridade e UF</div>', unsafe_allow_html=True)
col_g1, col_g2 = st.columns([1, 1])

with col_g1:
    pri_count = df_filtrado['prioridade'].value_counts().reindex(
        ['Muito Alta','Alta','Media','Baixa'], fill_value=0).reset_index()
    pri_count.columns = ['Prioridade','Quantidade']
    fig_pri = px.bar(
        pri_count, x='Prioridade', y='Quantidade',
        color='Prioridade',
        color_discrete_map=COR_PRI,
        text='Quantidade',
        title='Distribuição por Prioridade'
    )
    fig_pri.update_traces(texttemplate='%{text:,}', textposition='outside')
    fig_pri.update_layout(showlegend=False, height=350, margin=dict(t=40,b=20))
    st.plotly_chart(fig_pri, use_container_width=True)

with col_g2:
    uf_pri = df_filtrado.groupby(['uf_rfb','prioridade']).size().reset_index(name='n')
    fig_uf = px.bar(
        uf_pri, x='uf_rfb', y='n',
        color='prioridade',
        color_discrete_map=COR_PRI,
        title='Distribuição por UF e Prioridade',
        labels={'uf_rfb':'UF','n':'CNPJs','prioridade':'Prioridade'},
        category_orders={'prioridade':['Muito Alta','Alta','Media','Baixa']}
    )
    fig_uf.update_layout(height=350, margin=dict(t=40,b=20), legend_title='Prioridade')
    st.plotly_chart(fig_uf, use_container_width=True)

# ===== GRAFICOS LINHA 2 =====
st.markdown('<div class="section-title">📈 Score e Perfil Cadastral</div>', unsafe_allow_html=True)
col_g3, col_g4 = st.columns([1, 1])

with col_g3:
    fig_hist = px.histogram(
        df_filtrado, x='score_alto_valor', nbins=40,
        color_discrete_sequence=['#2E75B6'],
        title='Distribuição do Score (Alto Valor)',
        labels={'score_alto_valor':'Score','count':'CNPJs'}
    )
    fig_hist.add_vline(x=0.60, line_dash='dash', line_color='#1E7145',
        annotation_text='Alta (0.60)', annotation_position='top right')
    fig_hist.add_vline(x=0.75, line_dash='dash', line_color='#C55A11',
        annotation_text='Muito Alta (0.75)', annotation_position='top right')
    fig_hist.update_layout(height=350, margin=dict(t=40,b=20))
    st.plotly_chart(fig_hist, use_container_width=True)

with col_g4:
    porte_pri = df_filtrado.groupby(['Porte','prioridade']).size().reset_index(name='n')
    fig_porte = px.bar(
        porte_pri, x='Porte', y='n',
        color='prioridade',
        color_discrete_map=COR_PRI,
        title='Distribuição por Porte e Prioridade',
        labels={'Porte':'Porte','n':'CNPJs','prioridade':'Prioridade'},
        category_orders={'prioridade':['Muito Alta','Alta','Media','Baixa']}
    )
    fig_porte.update_layout(height=350, margin=dict(t=40,b=20), legend_title='Prioridade')
    st.plotly_chart(fig_porte, use_container_width=True)

# ===== MAPA =====
st.markdown('<div class="section-title">🗺️ Distribuição Geográfica</div>', unsafe_allow_html=True)

# Limites geograficos dos Top 5 UFs (SP, RJ, MG, PR, RS)
LAT_BOUNDS = (-33.8, -14.2)
LON_BOUNDS = (-54.0, -39.5)

df_mapa = df_filtrado[
    df_filtrado['prioridade'].isin(['Muito Alta','Alta']) &
    df_filtrado['uf_rfb'].isin(UFS_TOP5)
].copy()

if 'latitude' in df_mapa.columns and 'longitude' in df_mapa.columns and len(df_mapa) > 0:
    df_mapa = df_mapa.dropna(subset=['latitude','longitude'])
    df_mapa = df_mapa[
        df_mapa['latitude'].between(*LAT_BOUNDS) &
        df_mapa['longitude'].between(*LON_BOUNDS)
    ]
    if len(df_mapa) > 5000:
        df_mapa = df_mapa.sample(5000, random_state=42)

    fig_mapa = px.scatter_mapbox(
        df_mapa,
        lat='latitude', lon='longitude',
        color='prioridade',
        color_discrete_map=COR_PRI,
        size_max=8,
        zoom=4.5,
        center={'lat': -23.5, 'lon': -46.5},
        mapbox_style='carto-positron',
        title=f'CNPJs de Alta e Muito Alta Prioridade — {aba} (MG, PR, RJ, RS, SP)',
        hover_data={'Razao_Social': True, 'uf_rfb': True,
                    'score_alto_valor': True, 'Porte': True,
                    'latitude': False, 'longitude': False},
        labels={'prioridade':'Prioridade','score_alto_valor':'Score'}
    )
    fig_mapa.update_layout(height=500, margin=dict(t=40,b=20))
    st.plotly_chart(fig_mapa, use_container_width=True)
else:
    st.info("Mapa disponível quando os parquets reais contiverem colunas de latitude/longitude.")

# ===== SCORE MEDIO POR UF =====
st.markdown('<div class="section-title">📍 Score Médio por UF</div>', unsafe_allow_html=True)
score_uf = df_filtrado.groupby('uf_rfb')['score_alto_valor'].agg(['mean','count']).reset_index()
score_uf.columns = ['UF','Score Médio','CNPJs']
score_uf = score_uf.sort_values('Score Médio', ascending=False)

fig_score_uf = px.bar(
    score_uf, x='UF', y='Score Médio',
    text='Score Médio',
    color='Score Médio',
    color_continuous_scale=['#D6E4F0','#1F4E79'],
    title='Score Médio por UF',
)
fig_score_uf.update_traces(texttemplate='%{text:.3f}', textposition='outside')
fig_score_uf.update_layout(height=320, margin=dict(t=40,b=20), coloraxis_showscale=False)
st.plotly_chart(fig_score_uf, use_container_width=True)

# ===== TABELA =====
st.markdown('<div class="section-title">📋 Lista Priorizada</div>', unsafe_allow_html=True)

# --- Filtros inline da tabela ---
with st.expander("🔎 Filtros da tabela", expanded=True):
    col_f1, col_f2, col_f3, col_f4, col_f5, col_f6 = st.columns([1.4, 1.1, 1.1, 1.8, 0.9, 1.2])

    with col_f1:
        ufs_tab = sorted(df_filtrado['uf_rfb'].dropna().unique().tolist())
        ufs_tab_sel = st.multiselect(
            "UF", ufs_tab, default=ufs_tab, key="tab_uf",
            placeholder="Selecione as opções",
            help="Filtrar por estado na tabela"
        )
    with col_f2:
        portes_tab = sorted(df_filtrado['Porte'].dropna().unique().tolist())
        portes_tab_sel = st.multiselect(
            "Porte", portes_tab, default=portes_tab, key="tab_porte",
            placeholder="Selecione as opções"
        )
    with col_f3:
        pris_tab = ['Muito Alta', 'Alta', 'Media', 'Baixa']
        pris_tab_sel = st.multiselect(
            "Prioridade", pris_tab, default=['Muito Alta', 'Alta'], key="tab_pri",
            placeholder="Selecione as opções"
        )
    with col_f4:
        munis_tab = sorted(df_filtrado['municipio_rfb'].dropna().unique().tolist())
        munis_tab_sel = st.multiselect(
            "Município", munis_tab, default=munis_tab, key="tab_mun",
            placeholder="Selecione as opções",
            help="Filtrar por município na tabela"
        )
    with col_f5:
        n_exibir = st.selectbox("Exibir", [50, 100, 200, 500, 1000], index=0, key="tab_n")
    with col_f6:
        agrupar_cnpj_basico = st.checkbox(
            "Agrupar por CNPJ Básico",
            value=False,
            key="tab_grupo",
            help=(
                "Agrupa todos os estabelecimentos de uma mesma empresa pelo CNPJ Básico "
                "(8 primeiros dígitos). Exibe o maior score, prioridade mais alta e "
                "quantidade de estabelecimentos por grupo."
            )
        )

# --- Aplicar filtros da tabela ---
df_tabela = df_filtrado.copy()
df_tabela = df_tabela[
    df_tabela['uf_rfb'].isin(ufs_tab_sel) &
    df_tabela['Porte'].isin(portes_tab_sel) &
    df_tabela['prioridade'].isin(pris_tab_sel) &
    df_tabela['municipio_rfb'].isin(munis_tab_sel)
]

# --- Agrupamento por CNPJ Basico ---
ORDEM_PRI = {'Muito Alta': 0, 'Alta': 1, 'Media': 2, 'Baixa': 3}

if agrupar_cnpj_basico and 'cnpj_basico' in df_tabela.columns:
    df_grupo = (
        df_tabela.sort_values('score_alto_valor', ascending=False)
        .groupby('cnpj_basico', as_index=False)
        .agg(
            Razao_Social     = ('Razao_Social',    'first'),
            CNAE_Principal   = ('CNAE_Principal',  'first'),
            Porte            = ('Porte',           'first'),
            uf_rfb           = ('uf_rfb',          'first'),
            municipio_rfb    = ('municipio_rfb',   'first'),
            capital_social   = ('capital_social',  'max'),
            score_alto_valor = ('score_alto_valor','max'),
            qtd_estabelec    = ('cnpj',            'count'),
        )
    )
    # Recalcular prioridade com base no score consolidado do grupo
    df_grupo['prioridade'] = pd.cut(
        df_grupo['score_alto_valor'],
        bins=[0, 0.4, 0.6, 0.75, 1.01],
        labels=['Baixa', 'Media', 'Alta', 'Muito Alta']
    )
    df_tabela = df_grupo.sort_values('score_alto_valor', ascending=False).head(n_exibir)
    # Ofuscar razao social no modo agrupado
    df_tabela = ofuscar_razao_social_grupo(df_tabela)
    colunas_exibir = ['Razao_Social','CNAE_Principal','CNAE_Desc','Porte','uf_rfb',
                      'municipio_rfb','capital_social','score_alto_valor','prioridade','qtd_estabelec']
    rename_map = {
        'Razao_Social':'Razão Social', 'CNAE_Principal':'Atividade Econômica',
        'CNAE_Desc':'Descrição da Atividade Econômica',
        'uf_rfb':'UF', 'municipio_rfb':'Município', 'capital_social':'Capital Social',
        'score_alto_valor':'Score', 'prioridade':'Prioridade', 'qtd_estabelec':'Estabelecimentos'
    }
else:
    df_tabela = df_tabela.sort_values('score_alto_valor', ascending=False).head(n_exibir)
    colunas_exibir = ['Razao_Social','CNAE_Principal','CNAE_Desc','Porte','uf_rfb',
                      'municipio_rfb','capital_social','score_alto_valor','prioridade']
    rename_map = {
        'Razao_Social':'Razão Social', 'CNAE_Principal':'Atividade Econômica',
        'CNAE_Desc':'Descrição da Atividade Econômica',
        'uf_rfb':'UF', 'municipio_rfb':'Município', 'capital_social':'Capital Social',
        'score_alto_valor':'Score', 'prioridade':'Prioridade'
    }

# --- Contador inline ---
col_info1, col_info2, col_info3 = st.columns(3)
with col_info1:
    label_cnt = "empresas" if agrupar_cnpj_basico else "CNPJs"
    st.caption(f"**{len(df_tabela):,}** {label_cnt} exibidos")
with col_info2:
    n_ma_tab = (df_tabela['prioridade'] == 'Muito Alta').sum()
    n_a_tab  = (df_tabela['prioridade'] == 'Alta').sum()
    st.caption(f"Muito Alta: **{n_ma_tab:,}** | Alta: **{n_a_tab:,}**")
with col_info3:
    score_tab = df_tabela['score_alto_valor'].mean() if len(df_tabela) > 0 else 0
    st.caption(f"Score médio: **{score_tab:.4f}**")

# ===== MODAL DE DADOS CADASTRAIS =====
@st.dialog("Dados Cadastrais", width="large")
def modal_cadastro(row):
    def ofuscar(valor):
        if not valor or str(valor).strip() in ("", "nan", "None"):
            return "—"
        s = str(valor).strip()
        metade = max(2, len(s) // 2)
        return s[:metade] + " ****"

    def v(cols, ofusc=False):
        for c in (cols if isinstance(cols, list) else [cols]):
            val = row.get(c)
            if val is not None and str(val).strip() not in ("", "nan", "None"):
                return ofuscar(str(val)) if ofusc else str(val)
        return "—"

    st.markdown(f"### {v('Razao_Social')}")

    # Ofuscamento de CNPJ — obter valores via v() antes de formatar
    cnpj_raw   = v('cnpj')
    basico_raw = v('cnpj_basico')

    if cnpj_raw != '—':
        cnpj_digits = ''.join(filter(str.isdigit, cnpj_raw)).zfill(14)
        cnpj_fmt = f"{cnpj_digits[:2]}.***.***/****-{cnpj_digits[-2:]}"
    else:
        cnpj_fmt = '—'

    if basico_raw != '—':
        basico_digits = ''.join(filter(str.isdigit, basico_raw)).zfill(8)
        basico_fmt = f"{basico_digits[:2]}.***{basico_digits[-3:]}"
    else:
        basico_fmt = '—'

    st.markdown(f"**CNPJ:** `{cnpj_fmt}`  |  **CNPJ Básico:** `{basico_fmt}`")
    st.divider()

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("#### Identificação")
        st.markdown(f"**Porte:** {v('Porte')}")
        st.markdown(f"**Natureza Jurídica:** {v('Natureza_Juridica')}")
        st.markdown(f"**Situação Cadastral:** {v('Situacao_Cadastral')}")
        st.markdown(f"**Data de Abertura:** {v('Data_Inicio_Atividade')}")
        st.markdown(f"**Idade (anos):** {v('idade_empresa_anos')}")
        cap = row.get("capital_social", 0) or 0
        st.markdown(f"**Capital Social:** R$ {float(cap):,.2f}")
        st.markdown(f"**Região:** {v('REGIAO')}")
    with c2:
        st.markdown("#### Atividade Econômica")
        st.markdown(f"**CNAE Principal:** {v('CNAE_Principal')}")
        desc = v("CNAE_Desc")
        if desc != "—":
            st.markdown(f"**Descrição:** {desc}")
        st.markdown(f"**CNAE Secundário:** {v('CNAE_Secundario')}")

    st.divider()
    c3, c4 = st.columns(2)
    with c3:
        st.markdown("#### Endereço _(parcialmente ofuscado)_")
        log  = v(["logradouro_rfb", "Logradouro"], ofusc=True)
        num  = v(["numero_rfb",     "Numero"])
        bai  = v(["bairro_rfb",     "Bairro"],     ofusc=True)
        cep  = v(["cep_rfb",        "CEP"])
        mun  = v("municipio_rfb")
        uf   = v("uf_rfb")
        st.markdown(f"**Logradouro:** {log}, {num}")
        st.markdown(f"**Bairro:** {bai}")
        st.markdown(f"**CEP:** {cep}")
        st.markdown(f"**Município / UF:** {mun} / {uf}")
    with c4:
        st.markdown("#### Contato")
        ddd = v("DDD_1"); tel = v("Telefone_1")
        # Ofuscar telefone: manter DDD e primeiros 4 digitos, ocultar resto
        if ddd != "—" and tel != "—":
            tel_vis = tel[:4] + "****" if len(tel) > 4 else "****"
            fone_fmt = f"({ddd}) {tel_vis}"
        else:
            fone_fmt = "—"
        st.markdown(f"**Telefone:** {fone_fmt}")
        # Ofuscar e-mail: manter primeiros 3 chars + dominio ofuscado
        email_raw = v("Email")
        if email_raw != "—" and "@" in email_raw:
            usuario, dominio = email_raw.split("@", 1)
            usr_vis = usuario[:3] + "****" if len(usuario) > 3 else "****"
            dom_parts = dominio.split(".")
            dom_vis = "****." + dom_parts[-1] if dom_parts else "****"
            email_fmt = f"{usr_vis}@{dom_vis}"
        else:
            email_fmt = email_raw
        st.markdown(f"**E-mail:** {email_fmt}")

    st.divider()
    c5, c6 = st.columns(2)
    with c5:
        st.markdown("#### Score do Modelo")
        score = float(row.get("score_alto_valor", 0) or 0)
        st.metric("Score Alto Valor", f"{score:.4f}")
        st.markdown(f"**Prioridade:** {v('prioridade')}")
        st.markdown(f"**Classificação:** {v('classe_prevista')}")
    with c6:
        st.markdown("#### Geolocalização")
        lat = row.get("latitude"); lon = row.get("longitude")
        if lat and str(lat) not in ("nan", "None"):
            st.markdown(f"**Latitude:** {float(lat):.6f}")
            st.markdown(f"**Longitude:** {float(lon):.6f}")
        else:
            st.markdown("_Coordenadas não disponíveis_")

# ===== TABELA =====
colunas_disp = [c for c in colunas_exibir if c in df_tabela.columns]
df_exib = df_tabela[colunas_disp].rename(columns=rename_map)

if "Capital Social" in df_exib.columns:
    df_exib["Capital Social"] = df_exib["Capital Social"].apply(lambda x: f"R$ {x:,.0f}")
if "Score" in df_exib.columns:
    df_exib["Score"] = df_exib["Score"].apply(lambda x: f"{x:.4f}")

col_cfg = {}
if "Atividade Econômica" in df_exib.columns and "Descrição da Atividade Econômica" in df_exib.columns:
    col_cfg["Atividade Econômica"] = st.column_config.TextColumn(
        label="Atividade Econômica",
        help="Código CNAE — veja a coluna ao lado para a descrição completa.",
        width="medium",
    )
    col_cfg["Descrição da Atividade Econômica"] = st.column_config.TextColumn(
        label="Descrição da Atividade Econômica",
        width="large",
    )

st.caption("💡 Selecione uma linha clicando no checkbox à esquerda para ver os dados cadastrais completos.")

event = st.dataframe(
    df_exib,
    use_container_width=True,
    height=420,
    column_config=col_cfg,
    on_select="rerun",
    selection_mode="single-row",
)

# Abrir modal ao selecionar linha pelo checkbox
if event.selection and event.selection.rows:
    idx = event.selection.rows[0]
    modal_cadastro(df_tabela.iloc[idx].to_dict())

# ===== EXPORT =====
st.markdown('<div class="section-title">⬇️ Exportar</div>', unsafe_allow_html=True)
col_e1, col_e2, col_e3 = st.columns(3)

colunas_export = [c for c in colunas_exibir if c in df_tabela.columns]

with col_e1:
    df_export_alta = df_tabela[df_tabela['prioridade'].isin(['Muito Alta','Alta'])].sort_values('score_alto_valor', ascending=False)
    csv_alta = df_export_alta[colunas_export].to_csv(index=False, encoding='utf-8-sig')
    st.download_button(
        label=f"⬇️ Alta + Muito Alta ({len(df_export_alta):,} {'empresas' if agrupar_cnpj_basico else 'CNPJs'})",
        data=csv_alta,
        file_name=f"prioridade_alta_{aba.lower()}_{pd.Timestamp.now().strftime('%Y%m%d')}.csv",
        mime='text/csv',
        use_container_width=True
    )

with col_e2:
    csv_tabela = df_tabela[colunas_export].sort_values('score_alto_valor', ascending=False).to_csv(index=False, encoding='utf-8-sig')
    st.download_button(
        label=f"⬇️ Tabela filtrada ({len(df_tabela):,} {'empresas' if agrupar_cnpj_basico else 'CNPJs'})",
        data=csv_tabela,
        file_name=f"tabela_filtrada_{aba.lower()}_{pd.Timestamp.now().strftime('%Y%m%d')}.csv",
        mime='text/csv',
        use_container_width=True
    )

with col_e3:
    st.info(
        f"**{len(df_export_alta):,}** Alta+Muito Alta  \n"
        f"**{len(df_tabela):,}** na tabela filtrada"
    )

# ===== RODAPE =====
st.markdown("---")
st.markdown(
    "<small>MBA Engenharia de Dados — Universidade Presbiteriana Mackenzie  |  "
    "Modelo: XGBoost Exp. E  |  F1 Macro: 0.7585  |  "
    "Top 5 UFs: MG, PR, RJ, RS, SP  |  Versão 2 — dados corrigidos</small>",
    unsafe_allow_html=True
)
