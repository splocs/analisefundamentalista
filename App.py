import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import date
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Configurando a largura da página
st.set_page_config(layout="wide")

# Função para formatar a data
def formatar_data(data):
    return data.strftime('%d-%m-%Y')

# Função para pegar os dados das ações
@st.cache_data
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

# Exibir título do aplicativo
st.title('Análise de ações')

# Pegando os dados das ações
df = pegar_dados_acoes()
acao = df['snome']

nome_acao_escolhida = st.sidebar.selectbox('Escolha uma ação:', acao)
df_acao = df[df['snome'] == nome_acao_escolhida]
sigla_acao_escolhida = df_acao.iloc[0]['sigla_acao']
sigla_acao_escolhida += '.SA'

# Pegando os valores online
df_valores = pegar_valores_online(sigla_acao_escolhida)

# Criando o objeto Ticker
try:
    acao_escolhida = yf.Ticker(sigla_acao_escolhida)
    info = acao_escolhida.info
except Exception as e:
    st.error(f"Erro ao criar o objeto Ticker para {sigla_acao_escolhida}: {e}")

# Exibir informações detalhadas da ação
st.subheader('Informações Básicas do Ativo')

# Informações básicas do ativo
nome_acao = info.get('longName', 'N/A')
endereco = info.get('address1', 'N/A')
cidade = info.get('city', 'N/A')
estado = info.get('state', 'N/A')
pais = info.get('country', 'N/A')
site = info.get('website', 'N/A')
setor = info.get('sector', 'N/A')
subsetor = info.get('industry', 'N/A')

st.write(f"**{nome_acao} ({sigla_acao_escolhida})**")
st.write(f"{endereco}")
st.write(f"{cidade}, {estado}")
st.write(f"{pais}")
st.write(f"[{site}]({site})")
st.write(f"**Setor:** {setor}")
st.write(f"**Subsetor:** {subsetor}")

# Valor atual e porcentagem de variação
valor_atual = info.get('currentPrice', 'N/A')
mudanca = info.get('regularMarketChangePercent', 'N/A')

st.subheader('Valor Atual')
try:
    st.write(f"**{valor_atual}** {float(mudanca):.2f}%")
except ValueError:
    st.write(f"**{valor_atual}** {mudanca}")

# Descrição da empresa
descricao = info.get('longBusinessSummary', 'N/A')
st.subheader('Descrição')
st.write(descricao)

# Próximos eventos
eventos_proximos = info.get('earnings', {}).get('nextEarningsDate', 'N/A')
st.subheader('Próximos Eventos')
st.write(eventos_proximos)

# Eventos recentes
st.subheader('Eventos Recentes')
eventos_recentes = info.get('earnings', {}).get('earningsDate', [])
for evento in eventos_recentes:
    st.write(evento)

# Gráfico de candles interativo
st.subheader('Gráfico de Negociações')
df_valores = df_valores.rename(columns={
    'Date': 'Data',
    'Open': 'Abertura',
    'High': 'Alta',
    'Low': 'Baixa',
    'Close': 'Fechamento',
    'Adj Close': 'Fechamento Ajustado',
    'Volume': 'Volume'
})
fig = make_subplots(specs=[[{"secondary_y": True}]])
fig.add_trace(go.Candlestick(
    x=df_valores['Data'],
    open=df_valores['Abertura'],
    high=df_valores['Alta'],
    low=df_valores['Baixa'],
    close=df_valores['Fechamento'],
    name='Candlestick'
))
fig.add_trace(go.Bar(
    x=df_valores['Data'],
    y=df_valores['Volume'],
    name='Volume',
    marker_color='green'
), secondary_y=True)
fig.update_layout(title='Gráfico de Candles', xaxis_title='Data', yaxis_title='Preço', yaxis2_title='Volume')
st.plotly_chart(fig)

# Dados adicionais abaixo do gráfico
st.write(f"**Previous Close:** {info.get('previousClose', 'N/A')}")
st.write(f"**Open:** {info.get('open', 'N/A')}")
st.write(f"**Day's Range:** {info.get('dayLow', 'N/A')} - {info.get('dayHigh', 'N/A')}")
st.write(f"**52 Week Range:** {info.get('fiftyTwoWeekLow', 'N/A')} - {info.get('fiftyTwoWeekHigh', 'N/A')}")
st.write(f"**Volume:** {info.get('volume', 'N/A')}")
st.write(f"**Avg. Volume:** {info.get('averageVolume', 'N/A')}")
st.write(f"**Market Cap (intraday):** {info.get('marketCap', 'N/A')}")
st.write(f"**Beta (5Y Monthly):** {info.get('beta', 'N/A')}")
st.write(f"**PE Ratio (TTM):** {info.get('trailingPE', 'N/A')}")
st.write(f"**EPS (TTM):** {info.get('epsTrailingTwelveMonths', 'N/A')}")
st.write(f"**Earnings Date:** {info.get('earnings', {}).get('nextEarningsDate', 'N/A')}")
st.write(f"**Forward Dividend & Yield:** {info.get('dividendRate', 'N/A')} ({info.get('dividendYield', 'N/A')}%)")
st.write(f"**Ex-Dividend Date:** {info.get('exDividendDate', 'N/A')}")
st.write(f"**1y Target Est:** {info.get('targetMeanPrice', 'N/A')}")

# Seletor para alterar entre dados anuais e trimestrais
st.subheader('Resultados Financeiros')
periodo_financeiro = st.radio("Selecionar período financeiro", ["Anual", "Trimestral"])
period = 'annual' if periodo_financeiro == "Anual" else 'quarterly'

# Tabelas financeiras
st.subheader('Income Statement')
if period == 'annual':
    st.write(acao_escolhida.financials)
else:
    st.write(acao_escolhida.quarterly_financials)

st.subheader('Balance Sheet')
if period == 'annual':
    st.write(acao_escolhida.balance_sheet)
else:
    st.write(acao_escolhida.quarterly_balance_sheet)

st.subheader('Cash Flow')
if period == 'annual':
    st.write(acao_escolhida.cashflow)
else:
    st.write(acao_escolhida.quarterly_cashflow)

# Indicadores Fundamentalistas
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
    "ROIC": info.get("returnOnEquity", "N/A"),
    "Div. Yield": info.get("dividendYield", "N/A"),
    "ROE": info.get("returnOnAssets", "N/A"),
    "EV / EBITDA": info.get("enterpriseToEbitda", "N/A"),
    "Liquidez Corr": info.get("currentRatio", "N/A"),
    "EV / EBIT": info.get("enterpriseToEbitda", "N/A"),
    "Div Br/ Patrim": info.get("debtToEquity", "N/A"),
    "Cres. Rec (5a)": info.get("revenueGrowth", "N/A"),
    "Div. Br/ EBITDA": info.get("debtToEbitda", "N/A"),
    "Cres. Lucros (5a)": info.get("earningsGrowth", "N/A"),
    "Giro Ativos": info.get("assetTurnover", "N/A"),
    "Beta": info.get("beta", "N/A")
}

df_indicadores = pd.DataFrame(list(indicadores.items()), columns=["Indicador", "Valor"])
st.dataframe(df_indicadores)

# Explicações detalhadas para investidores leigos
st.subheader('Explicação dos Indicadores')

explicacoes = {
    "P/L": "Preço sobre Lucro (P/L) indica quantos anos o investidor levaria para recuperar o capital investido.",
    "LPA": "Lucro por Ação (LPA) representa o lucro líquido dividido pelo número de ações emitidas.",
    "P/VP": "Preço sobre Valor Patrimonial (P/VP) indica se uma ação está cara ou barata comparada ao valor patrimonial da empresa.",
    "VPA": "Valor Patrimonial por Ação (VPA) é o valor do patrimônio líquido dividido pelo número de ações emitidas.",
    "P/EBIT": "Preço sobre Lucro antes de Juros e Impostos (P/EBIT) mostra a relação entre o preço da ação e o EBIT.",
    "Marg. Bruta": "Margem Bruta é a porcentagem do lucro bruto sobre a receita líquida.",
    "PSR": "Preço sobre Receita (PSR) indica quanto os investidores estão pagando por cada unidade monetária de receita.",
    "Marg. EBIT": "Margem EBIT é a porcentagem do EBIT sobre a receita líquida.",
    "P/Ativos": "Preço sobre Ativos mostra a relação entre o preço da ação e os ativos totais da empresa.",
    "Marg. Líquida": "Margem Líquida é a porcentagem do lucro líquido sobre a receita líquida.",
    "P/Cap. Giro": "Preço sobre Capital de Giro indica quanto os investidores estão pagando pelo capital de giro da empresa.",
    "EBIT / Ativo": "EBIT sobre Ativos mostra a eficiência da empresa em gerar lucro com seus ativos.",
    "P/Ativ Circ Liq": "Preço sobre Ativos Circulantes Líquidos mostra a relação entre o preço da ação e os ativos circulantes líquidos.",
    "ROIC": "Retorno sobre o Capital Investido (ROIC) mede a eficiência da empresa em gerar lucro com o capital investido.",
    "Div. Yield": "Dividend Yield é a porcentagem de retorno em dividendos sobre o preço da ação.",
    "ROE": "Retorno sobre Patrimônio (ROE) indica a rentabilidade do patrimônio líquido.",
    "EV / EBITDA": "Valor da Empresa sobre EBITDA (EV/EBITDA) mostra a relação entre o valor da empresa e o EBITDA.",
    "Liquidez Corr": "Liquidez Corrente é a relação entre os ativos circulantes e os passivos circulantes.",
    "EV / EBIT": "Valor da Empresa sobre EBIT (EV/EBIT) mostra a relação entre o valor da empresa e o EBIT.",
    "Div Br/ Patrim": "Dívida Bruta sobre Patrimônio mostra a relação entre a dívida bruta e o patrimônio líquido.",
    "Cres. Rec (5a)": "Crescimento da Receita em 5 anos mostra a taxa de crescimento anual da receita nos últimos 5 anos.",
    "Div. Br/ EBITDA": "Dívida Bruta sobre EBITDA mostra a relação entre a dívida bruta e o EBITDA.",
    "Cres. Lucros (5a)": "Crescimento dos Lucros em 5 anos mostra a taxa de crescimento anual dos lucros nos últimos 5 anos.",
    "Giro Ativos": "Giro dos Ativos mostra a eficiência da empresa em usar seus ativos para gerar receita.",
    "Beta": "Beta mede a volatilidade da ação em relação ao mercado. Um beta maior que 1 indica maior volatilidade."
}

for indicador, explicacao in explicacoes.items():
    st.write(f"**{indicador}:** {explicacao}")


for indicador, explicacao in explicacoes.items():
    st.write(f"**{indicador}:** {explicacao}")


