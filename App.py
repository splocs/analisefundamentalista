import streamlit as st
import pandas as pd
import yfinance as yf
from PIL import Image
from datetime import date
import plotly.express as px

# Configurando a largura da página
st.set_page_config(layout="wide")

# Função para formatar a data
def formatar_data(data):
    return data.strftime('%d-%m-%Y')

# Dicionário de tradução de nomes das colunas
traducao = {
    'Date': 'Data',
    'Open': 'Abertura',
    'High': 'Alta',
    'Low': 'Baixa',
    'Close': 'Fechamento',
    'Adj Close': 'Fechamento Ajustado',
    'Volume': 'Volume'
}

# Função para pegar os dados das ações
@st.cache
def pegar_dados_acoes():
    path = 'https://raw.githubusercontent.com/splocs/meu-repositorio/main/acoes.csv'
    return pd.read_csv(path, delimiter=';')

# Função para pegar os valores online
def pegar_valores_online(sigla_acao):
    df = yf.download(sigla_acao, DATA_INICIO, DATA_FIM, progress=False)
    df.reset_index(inplace=True)
    return df

# Definindo data de início e fim
DATA_INICIO = '2017-01-01'
DATA_FIM = date.today().strftime('%Y-%m-%d')

# Logo
logo_path = "logo.png"
logo = Image.open(logo_path)

# Exibir o logo no aplicativo Streamlit
st.image(logo, width=250)

# Exibir o logo na sidebar
st.sidebar.image(logo, width=150)

st.title('Análise de ações')

# Criando a sidebar
st.sidebar.markdown('Escolha a ação')
n_dias = st.sidebar.slider('Quantidade de dias de previsão', 30, 365)

# Pegando os dados das ações
df = pegar_dados_acoes()
acao = df['snome']

nome_acao_escolhida = st.sidebar.selectbox('Escolha uma ação:', acao)
df_acao = df[df['snome'] == nome_acao_escolhida]
sigla_acao_escolhida = df_acao.iloc[0]['sigla_acao']
sigla_acao_escolhida += '.SA'

# Pegando os valores online
df_valores = pegar_valores_online(sigla_acao_escolhida)

st.subheader('Tabela de Valores - ' + nome_acao_escolhida)

# Renomeando as colunas usando o dicionário de tradução
df_valores = df_valores.rename(columns=traducao)

# Convertendo a coluna "Data" para o formato desejado
df_valores['Data'] = df_valores['Data'].dt.strftime('%d-%m-%Y')
st.write(df_valores.tail(40))

# Criando o objeto Ticker
try:
    acao_escolhida = yf.Ticker(sigla_acao_escolhida)
except Exception as e:
    st.error(f"Erro ao criar o objeto Ticker para {sigla_acao_escolhida}: {e}")

# Função para exibir dados com tratamento de exceção
def exibir_dados(label, func):
    try:
        dados = func()
        if dados is not None and not dados.empty:
            st.write(f"**{label}:**")
            st.write(dados)
    except Exception as e:
        st.warning(f"{label} não disponível: {e}")

# Coletando e exibindo dados fundamentalistas
exibir_dados("Histórico de preços", lambda: acao_escolhida.history(period="max"))
exibir_dados("Dividendos", lambda: acao_escolhida.dividends)
exibir_dados("Splits de ações", lambda: acao_escolhida.splits)
exibir_dados("Balanço patrimonial", lambda: acao_escolhida.balance_sheet)
exibir_dados("Demonstração de resultados", lambda: acao_escolhida.financials)
exibir_dados("Fluxo de caixa", lambda: acao_escolhida.cashflow)
exibir_dados("Recomendações de analistas", lambda: acao_escolhida.recommendations)
exibir_dados("Informações Básicas", lambda: acao_escolhida.news)

# Gráficos para visualização de dados financeiros
st.subheader('Gráficos')

# Gráfico de Preços de Fechamento
fig = px.line(df_valores, x='Data', y='Fechamento', title='Preços de Fechamento ao Longo do Tempo')
st.plotly_chart(fig)

# Gráfico de Volume
fig2 = px.bar(df_valores, x='Data', y='Volume', title='Volume de Negociação ao Longo do Tempo')
st.plotly_chart(fig2)

# Gráfico de Dividendos
if not acao_escolhida.dividends.empty:
    fig3 = px.line(acao_escolhida.dividends, title='Histórico de Dividendos')
    st.plotly_chart(fig3)

# Gráfico de Balanço Patrimonial
if not acao_escolhida.balance_sheet.empty:
    fig4 = px.bar(acao_escolhida.balance_sheet, title='Balanço Patrimonial')
    st.plotly_chart(fig4)

# Gráfico de Demonstração de Resultados
if not acao_escolhida.financials.empty:
    fig5 = px.bar(acao_escolhida.financials, title='Demonstração de Resultados')
    st.plotly_chart(fig5)

# Gráfico de Fluxo de Caixa
if not acao_escolhida.cashflow.empty:
    fig6 = px.bar(acao_escolhida.cashflow, title='Fluxo de Caixa')
    st.plotly_chart(fig6)

