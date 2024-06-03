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
def exibir_dados(label, func, period):
    try:
        dados = func(period=period)
        if dados is not None and not dados.empty:
            st.write(f"**{label}:**")
            st.write(dados)
    except Exception as e:
        st.warning(f"{label} não disponível: {e}")

# Exibir informações detalhadas da ação
st.subheader('Informações Detalhadas da Ação')

info = acao_escolhida.info
dados_detalhados = {
    "Papel": sigla_acao_escolhida,
    "Cotação": info.get("currentPrice", "N/A"),
    "Tipo": "Ordinária" if info.get("quoteType", "N/A") == "EQUITY" else "Preferencial",
    "Data últ cotação": formatar_data(date.today()),
    "Empresa": info.get("shortName", "N/A"),
    "Min 52 semanas": info.get("fiftyTwoWeekLow", "N/A"),
    "Setor": info.get("sector", "N/A"),
    "Max 52 semanas": info.get("fiftyTwoWeekHigh", "N/A"),
    "Subsetor": info.get("industry", "N/A"),
    "Vol $ méd (2m)": info.get("averageVolume", "N/A"),
    "Valor de mercado": info.get("marketCap", "N/A"),
    "Últ balanço processado": formatar_data(date.today()),  # Deve ser ajustado conforme disponibilidade
    "Valor da firma": info.get("enterpriseValue", "N/A"),
    "Nro. Ações": info.get("sharesOutstanding", "N/A"),
}

st.write(pd.DataFrame(dados_detalhados.items(), columns=["Descrição", "Valor"]))

# Exibir Indicadores Fundamentalistas
st.subheader('Indicadores Fundamentalistas')

indicadores = {
    "P/L": info.get("trailingPE", "N/A"),
    "LPA": info.get("epsTrailingTwelveMonths", "N/A"),
    "P/VP": info.get("priceToBook", "N/A"),
    "VPA": info.get("bookValue", "N/A"),
    "P/EBIT": info.get("enterpriseToEbitda", "N/A"),
    "Marg. Bruta": info.get("grossMargins", "N/A"),
    "PSR": info.get("priceToSalesTrailing12Months", "N/A"),
    "Marg. EBIT": info.get("ebitdaMargins", "N/A"),
    "P/Ativos": info.get("totalAssets", "N/A"),
    "Marg. Líquida": info.get("profitMargins", "N/A"),
    "P/Cap. Giro": info.get("currentRatio", "N/A"),
    "EBIT / Ativo": info.get("ebitda", "N/A"),
    "P/Ativ Circ Liq": info.get("enterpriseValue", "N/A"),
    "ROIC": info.get("returnOnAssets", "N/A"),
    "Div. Yield": info.get("dividendYield", "N/A"),
    "ROE": info.get("returnOnEquity", "N/A"),
    "EV / EBITDA": info.get("enterpriseToEbitda", "N/A"),
    "Liquidez Corr": info.get("currentRatio", "N/A"),
    "EV / EBIT": info.get("enterpriseToRevenue", "N/A"),
    "Div Br/ Patrim": info.get("debtToEquity", "N/A"),
    "Cres. Rec (5a)": info.get("revenueGrowth", "N/A"),
    "Giro Ativos": info.get("assetTurnover", "N/A")
}

st.write(pd.DataFrame(indicadores.items(), columns=["Indicador", "Valor"]))

# Dados do Balanço Patrimonial
st.subheader('Dados do Balanço Patrimonial')

balanco = {
    "Ativo": info.get("totalAssets", "N/A"),
    "Dív. Bruta": info.get("totalDebt", "N/A"),
    "Disponibilidades": info.get("cash", "N/A"),
    "Dív. Líquida": info.get("netDebt", "N/A"),
    "Ativo Circulante": info.get("currentAssets", "N/A"),
    "Patrim. Líq": info.get("totalStockholderEquity", "N/A")
}

st.write(pd.DataFrame(balanco.items(), columns=["Descrição", "Valor"]))


# Seletor para alterar entre dados anuais e trimestrais
periodo_financeiro = st.radio("Selecionar período financeiro", ["Anual", "Trimestral"])

# Coletando e exibindo dados fundamentalistas adicionais
period = 'annual' if periodo_financeiro == "Anual" else 'quarterly'
exibir_dados("Balanço patrimonial", lambda period: acao_escolhida.balance_sheet if period == 'annual' else acao_escolhida.quarterly_balance_sheet, period)
exibir_dados("Demonstração de resultados", lambda period: acao_escolhida.financials if period == 'annual' else acao_escolhida.quarterly_financials, period)
exibir_dados("Fluxo de caixa", lambda period: acao_escolhida.cashflow if period == 'annual' else acao_escolhida.quarterly_cashflow, period)
exibir_dados("Histórico de preços", lambda period: acao_escolhida.history(period="max"), period)
exibir_dados("Dividendos", lambda period: acao_escolhida.dividends, period)
exibir_dados("Splits de ações", lambda period: acao_escolhida.splits, period)
exibir_dados("Recomendações de analistas", lambda period: acao_escolhida.recommendations, period)
exibir_dados("Informações Básicas", lambda period: acao_escolhida.news, period)

# Gráficos usando Plotly
# Gráfico de Histórico de Preços
if not acao_escolhida.history(period="max").empty:
    fig1 = px.line(acao_escolhida.history(period="max"), title='Histórico de Preços')
    st.plotly_chart(fig1)

# Gráfico de Dividendos
if not acao_escolhida.dividends.empty:
    fig2 = px.bar(acao_escolhida.dividends, title='Dividendos')
    st.plotly_chart(fig2)

# Gráfico de Splits de Ações
if not acao_escolhida.splits.empty:
    fig3 = px.bar(acao_escolhida.splits, title='Splits de Ações')
    st.plotly_chart(fig3)

# Gráfico de Balanço Patrimonial
if not acao_escolhida.balance_sheet.empty:
    fig4 = px.bar(acao_escolhida.balance_sheet if period == 'annual' else acao_escolhida.quarterly_balance_sheet, title='Balanço Patrimonial')
    st.plotly_chart(fig4)

# Gráfico de Demonstração de Resultados
if not acao_escolhida.financials.empty:
    fig5 = px.bar(acao_escolhida.financials if period == 'annual' else acao_escolhida.quarterly_financials, title='Demonstração de Resultados')
    st.plotly_chart(fig5)

# Gráfico de Fluxo de Caixa
if not acao_escolhida.cashflow.empty:
    fig6 = px.bar(acao_escolhida.cashflow if period == 'annual' else acao_escolhida.quarterly_cashflow, title='Fluxo de Caixa')
    st.plotly_chart(fig6)


