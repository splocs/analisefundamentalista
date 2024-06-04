import streamlit as st
import pandas as pd
import yfinance as yf
from PIL import Image
from datetime import date
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Configurando a largura da página
st.set_page_config(layout="wide")
@@ -12,17 +12,6 @@
def formatar_data(data):
    return data.strftime('%d-%m-%Y')

# Dicionário de tradução de nomes das colunas
traducao = {
    'Date': 'Data',
    'Open': 'Abertura',
    'High': 'Alta',
    'Low': 'Baixa',
    '-lose': 'Fechamento',
    'Adj Close': 'Fechamento Ajustado',
    'Volume': 'Volume'
}

# Função para pegar os dados das ações
@st.cache
def pegar_dados_acoes():
@@ -35,30 +24,13 @@ def pegar_valores_online(sigla_acao):
    df.reset_index(inplace=True)
    return df

# Função para pegar o URL do logotipo da empresa
def pegar_logo_empresa(ticker):
    return f"https://logo.clearbit.com/{ticker}.com"

# Definindo data de início e fim
DATA_INICIO = '2017-01-01'
DATA_FIM = date.today().strftime('%Y-%m-%d')

# Logo padrão (se não houver logo da empresa)
logo_path = "logo.png"
logo_padrao = Image.open(logo_path)

# Exibir o logo padrão no aplicativo Streamlit
st.image(logo_padrao, width=250)

# Exibir o logo padrão na sidebar
st.sidebar.image(logo_padrao, width=150)

# Exibir título do aplicativo
st.title('Análise de ações')

# Criando a sidebar
st.sidebar.markdown('Escolha a ação')
n_dias = st.sidebar.slider('Quantidade de dias de previsão', 30, 365)

# Pegando os dados das ações
df = pegar_dados_acoes()
acao = df['snome']
@@ -71,65 +43,128 @@ def pegar_logo_empresa(ticker):
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
    info = acao_escolhida.info
    logo_url = info.get('logo_url', pegar_logo_empresa(sigla_acao_escolhida.split('.')[0].lower()))
except Exception as e:
    st.error(f"Erro ao criar o objeto Ticker para {sigla_acao_escolhida}: {e}")
    logo_url = None

# Exibir o logotipo da empresa selecionada
if logo_url:
    st.image(logo_url, width=250)
    st.sidebar.image(logo_url, width=150)

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
st.write(f"**{valor_atual}** {mudanca:.2f}%")

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

st.write(pd.DataFrame(dados_detalhados.items(), columns=["Descrição", "Valor"]))
# Seletor para alterar entre dados anuais e trimestrais
st.subheader('Resultados Financeiros')
periodo_financeiro = st.radio("Selecionar período financeiro", ["Anual", "Trimestral"])
period = 'annual' if periodo_financeiro == "Anual" else 'quarterly'

# Exibir Indicadores Fundamentalistas
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
@@ -152,68 +187,47 @@ def exibir_dados(label, func, period):
    "EV / EBIT": info.get("enterpriseToRevenue", "N/A"),
    "Div Br/ Patrim": info.get("debtToEquity", "N/A"),
    "Cres. Rec (5a)": info.get("revenueGrowth", "N/A"),
    "Giro Ativos": info.get("assetTurnover", "N/A")
    "Div. Br/ EBITDA": info.get("debtToEbitda", "N/A"),
    "Cres. Lucros (5a)": info.get("earningsGrowth", "N/A"),
    "Giro Ativos": info.get("assetTurnover", "N/A"),
    "Beta": info.get("beta", "N/A")
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

st.write(pd.DataFrame(balanco.items(), columns=["Descrição", "Valor"]))

# Seletor para alterar entre dados anuais e trimestrais
periodo_financeiro = st.radio("Selecionar período financeiro", ["Anual", "Trimestral"])

# Coletando e exibindo dados fundamentalistas adicionais
period = 'annual' if periodo_financeiro == "Anual" else 'quarterly'
for indicador, explicacao in explicacoes.items():
    st.write(f"**{indicador}:** {explicacao}")

exibir_dados("Histórico de preços", lambda period: acao_escolhida.history(period="max"), period)
exibir_dados("Dividendos", lambda period: acao_escolhida.dividends, period)
exibir_dados("Splits de ações", lambda period: acao_escolhida.splits, period)
exibir_dados("Balanço patrimonial", lambda period: acao_escolhida.balance_sheet if period == 'annual' else acao_escolhida.quarterly_balance_sheet, period)
exibir_dados("Demonstração de resultados", lambda period: acao_escolhida.financials if period == 'annual' else acao_escolhida.quarterly_financials, period)
exibir_dados("Fluxo de caixa", lambda period: acao_escolhida.cashflow if period == 'annual' else acao_escolhida.quarterly_cashflow, period)
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

