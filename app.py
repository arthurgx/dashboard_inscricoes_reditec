import streamlit as st
import pandas as pd
import plotly.express as px

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

fig = px.bar(
    contagem,
    x="Dominio",
    y="count",
    title="Inscritos por instituição"
)

st.plotly_chart(fig, use_container_width=True)