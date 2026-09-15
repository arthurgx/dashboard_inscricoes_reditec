import streamlit as st
import pandas as pd
import plotly.express as px

df = pd.DataFrame({
    "Mês": ["Jan","Fev","Mar","Abr","Mai","Jun"],
    "Vendas": [120, 145, 98, 200, 175, 230],
    "Clientes": [40, 55, 35, 80, 70, 95],
})

st.title("Painel de Vendas")

st.write("Resumo dos últimos 6 meses")

st.subheader("Dados brutos")
st.dataframe(df, use_container_width=True)

st.subheader("Vendas por Mês")
fig_bar = px.bar(df, x="Mês", y ="Vendas")
st.plotly_chart(fig_bar, use_container_width=True)

st.subheader("Tendência de Clientes")
fig_line = px.line(df, x="Mês", y="Clientes")
st.plotly_chart(fig_line, use_container_width=True)