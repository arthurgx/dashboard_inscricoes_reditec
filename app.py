import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(page_title="Painel", layout="wide")

DATA_PATH_REDITEC = "formulario.csv"

MULTI_SELECT_COLS = {
    "O que mais busca nesta Reditec?": "Busca dos participantes",
    "Quais temas você mais gostaria de ouvir e debater durante a Reditec?": "Temas de interesse",
}

FILTER_COLS = [
    "Instituição",
    "Identidade de Gênero",
    "Qual sua cor ou raça?",
    "Instância a que se vincula na Reditec",
    "Há quantas edições participa da Reditec?",
    "Categoria Inscrição",
]

INTEREST_COLS = {
    "Tem interesse em participar da Corrida da Reditec?": "Interesse na Corrida da Reditec",
    "Tem interesse em participar da confraternização por adesão?": "Interesse na Confraternização",
}


# ==================== Aba: Inscricoes ====================
def render_Inscricoes():
    df = pd.read_csv("inscricoes.csv")

    df["Dominio"] = df["Email"].str.split("@").str[1]
    df_if = df[df["Dominio"].str.startswith("if", na=False)]

    st.title("Dashboard de Inscrições - REDITEC")
    st.write("Análise dos inscritos na REDITEC")
    total_inscritos = len(df)
    st.metric("Total de inscritos", total_inscritos)

    st.subheader("Dados das inscrições")
    dados_exibição = df.drop(columns=["Dominio"])
    st.dataframe(dados_exibição, use_container_width=True)

    contagem = df_if["Dominio"].value_counts().reset_index()
    contagem["Dominio"] = (contagem["Dominio"].str.replace(".edu.br", "", regex=False).str.upper()
)

    fig = px.bar(
        contagem,
        x="Dominio",
        y="count",
        title="Inscritos por instituição"
    )

    st.plotly_chart(fig, use_container_width=True)
# ==================== Aba: Reditec ====================
@st.cache_data
def load_reditec_data():
    return pd.read_csv(DATA_PATH_REDITEC, encoding="utf-8-sig")
 
 
def split_multi(series: pd.Series) -> pd.Series:
    """Explode uma coluna de checkbox (opções separadas por ';') em uma linha por opção."""
    exploded = series.dropna().str.split(";").explode().str.strip()
    return exploded[exploded != ""]
 
 
def bar_from_counts(counts: pd.Series, title: str):
    counts = counts.sort_values(ascending=True)
    labels = counts.index.tolist()
    values = counts.values.tolist()
    y_pos = list(range(len(labels)))
    bar_width = 0.5  
 
    fig = go.Figure(
        go.Bar(
            x=values,
            y=y_pos,
            orientation="h",
            text=values,
            textposition="outside",
            textfont=dict(size=12),
            width=bar_width,
            cliponaxis=False,
        )
    )

    annotations = [
        dict(
            x=0,
            y=y + bar_width / 2 + 0.05,
            xref="x",
            yref="y",
            text=label,
            showarrow=False,
            xanchor="left",
            yanchor="bottom",
            font=dict(size=12),
        )
        for y, label in zip(y_pos, labels)
    ]
 
    fig.update_layout(
        title=title,
        annotations=annotations,
        yaxis=dict(
            showticklabels=False,
            showgrid=False,
            zeroline=False,
            range=[-0.6, len(labels) - 1 + 0.6],
        ),
        xaxis=dict(title="Nº de respostas"),
        height=max(360, 66 * len(labels)),
        margin=dict(l=10, r=50, t=60, b=10),
        showlegend=False,
    )
    return fig
 
 
SIM_NAO_COLORS = {"SIM": "#5DADE2", "NÃO": "#E74C3C"}


def pie_from_counts(counts: pd.Series, title: str, color_map: dict | None = None):
    labels = counts.index.tolist()
    colors = [color_map.get(lbl, "#5DADE2") for lbl in labels] if color_map else None
    fig = go.Figure(
        go.Pie(
            labels=labels,
            values=counts.values.tolist(),
            hole=0.45,
            textinfo="label+percent+value",
            marker=dict(colors=colors) if colors else {},
        )
    )
    fig.update_layout(
        title=title,
        margin=dict(l=10, r=10, t=60, b=10),
        height=380,
    )
    return fig


def render_reditec():
    df_raw = load_reditec_data()
 
    st.title("Dashboard Formulário de inscrições — Reditec")
 
    st.sidebar.header("Filtros — Reditec")
    df = df_raw.copy()
 
    for col in FILTER_COLS:
        if col not in df.columns:
            continue
        options = sorted(df[col].dropna().unique().tolist())
        selected = st.sidebar.multiselect(col, options, key=f"filtro_{col}")
        if selected:
            df = df[df[col].isin(selected)]
 
    st.sidebar.markdown(f"**{len(df)} inscrições** após filtro (de {len(df_raw)})")
 
    if df.empty:
        st.warning("Nenhuma inscrição corresponde aos filtros selecionados.")
        return
 
    st.header("Perguntas de múltipla escolha")
 
    col_a, col_b = st.columns(2)
    cols_ui = [col_a, col_b]
 
    for i, (col_name, label) in enumerate(MULTI_SELECT_COLS.items()):
        if col_name not in df.columns:
            continue
        counts = split_multi(df[col_name]).value_counts()
        with cols_ui[i % 2]:
            st.plotly_chart(bar_from_counts(counts, label), use_container_width=True)
            with st.expander("Ver tabela"):
                st.dataframe(counts.rename("Respostas"))
 
    st.header("Interesse em atividades extras")

    col_e, col_f = st.columns(2)
    interest_cols_ui = [col_e, col_f]

    for i, (col_name, label) in enumerate(INTEREST_COLS.items()):
        if col_name not in df.columns:
            continue
        counts = df[col_name].dropna().value_counts()
        with interest_cols_ui[i % 2]:
            st.plotly_chart(pie_from_counts(counts, label, color_map=SIM_NAO_COLORS), use_container_width=True)

    st.header("Perfil dos inscritos")
 
    col_c, col_d = st.columns(2)
    with col_c:
        if "Identidade de Gênero" in df.columns:
            counts = df["Identidade de Gênero"].dropna().value_counts()
            st.plotly_chart(bar_from_counts(counts, "Identidade de gênero"), use_container_width=True)
    with col_d:
        if "Há quantas edições participa da Reditec?" in df.columns:
            counts = df["Há quantas edições participa da Reditec?"].dropna().value_counts()
            st.plotly_chart(bar_from_counts(counts, "Edições da Reditec já participadas"), use_container_width=True)
 
    if "Instituição" in df.columns:
        counts = df["Instituição"].dropna().value_counts().head(20)
        st.plotly_chart(bar_from_counts(counts, "Top 20 instituições"), use_container_width=True)
 
 
# ==================== App principal ====================
tab_Inscricoes, tab_reditec = st.tabs(["Inscrições", "Formulário Reditec"])

with tab_Inscricoes:
    render_Inscricoes()

with tab_reditec:
    render_reditec()