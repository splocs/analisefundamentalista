import streamlit as st
import pandas as pd
import yfinance as yf
from PIL import Image
from datetime import date
import plotly.express as px


# Você pode usar uma biblioteca específica para acessar um calendário econômico, como 'investpy' por exemplo.investin.com atençao testar depois


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

# Logo padrão (se não houver logo da empresa)
logo_path = "logo.png"
logo_padrao = Image.open(logo_path)

# Exibir o logo padrão no aplicativo Streamlit
st.image(logo_padrao, width=250)

# Exibir o logo padrão na sidebar
st.sidebar.image(logo_padrao, width=150)

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
    info = acao_escolhida.info
except Exception as e:
    st.error(f"Erro ao criar o objeto Ticker para {sigla_acao_escolhida}: {e}")

# Exibir informações detalhadas da ação
st.subheader('Informações Detalhadas da Ação')

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
    "Patrim. Líq": info.get("totalStockholderEquity", "N/A"),
    "Variação da Média Trienal do Lucro Líquido (VarLL)": info.get("threeYearAverageReturn", "N/A"),
    "Índice Preço Lucro Médio (P/L)": info.get("trailingPE", "N/A"),
    "Índice Dívida Financeira de Curto Prazo / Dívida Financeira Total (PFCP/PFT)": info.get("shortRatio", "N/A"),
    "Liquidez Seca (LS)": info.get("quickRatio", "N/A"),
    "Ativo Total (AT)": info.get("totalAssets", "N/A"),
    "Liquidez Corrente (LC)": info.get("currentRatio", "N/A"),
    "Índice Preço Valor Patrimonial por Ação (P/VPA)": info.get("priceToBook", "N/A"),
    "Lucro por Ação (LPA)": info.get("eps", "N/A"),
    "Return on Assets (ROA)": info.get("returnOnAssets", "N/A"),
    "Crescimento da Receita": info.get("revenueGrowth", "N/A"),
    "Crescimento do Lucro": info.get("earningsGrowth", "N/A"),
    "PSR (Preço/Receita)": info.get("priceToSalesTrailing12Months", "N/A"),
    "Índice de Cobertura de Juros": info.get("interestCoverage", "N/A")
}

st.write(pd.DataFrame(balanco.items(), columns=["Descrição", "Valor"]))

# Seletor para alterar entre dados anuais e trimestrais
periodo_financeiro = st.radio("Selecionar período financeiro", ["Anual", "Trimestral"])

# Coletando e exibindo dados fundamentalistas adicionais
period = 'annual' if periodo_financeiro == "Anual" else 'quarterly'

# Função para exibir dados com tratamento de exceção
def exibir_dados(label, func, period):
    try:
        dados = func(period=period)
        if dados is not None and not dados.empty:
            st.write(f"**{label}:**")
            st.write(dados)
    except Exception as e:
        st.warning(f"{label} não disponível: {e}")

exibir_dados("Histórico de preços", lambda period: acao_escolhida.history(period="max"), period)
exibir_dados("Dividendos", lambda period: acao_escolhida.dividends, period)
exibir_dados("Splits de ações", lambda period: acao_escolhida.splits, period)
exibir_dados("Balanço patrimonial", lambda period: acao_escolhida.balance_sheet if period == 'annual' else acao_escolhida.quarterly_balance_sheet, period)
exibir_dados("Demonstração de resultados", lambda period: acao_escolhida.financials if period == 'annual' else acao_escolhida.quarterly_financials, period)
exibir_dados("Fluxo de caixa", lambda period: acao_escolhida.cashflow if period == 'annual' else acao_escolhida.quarterly_cashflow, period)
exibir_dados("Recomendações de analistas", lambda period: acao_escolhida.recommendations, period)
exibir_dados("Contratos de Opções", lambda period: acao_escolhida.options, period)

#outro teste

# Volume de Negociação
exibir_dados("Volume Médio", lambda period: acao_escolhida.history(period="max")['Volume'].mean(), period)
# Variação de Preço
exibir_dados("Variação de Preço", lambda period: acao_escolhida.history(period="max")['Close'].diff(), period)
# Percentual de Ganho/Perda
exibir_dados("Percentual de Ganho/Perda", lambda period: acao_escolhida.history(period="max")['Close'].pct_change(), period)


##ver se não tem duplicados

exibir_dados("Descrição da Empresa", lambda period: info.get('longBusinessSummary', 'N/A'), period)
exibir_dados("Setor da Empresa", lambda period: info.get('sector', 'N/A'), period)
exibir_dados("Subsetor da Empresa", lambda period: info.get('industry', 'N/A'), period)
exibir_dados("P/L (Preço/Lucro)", lambda period: info.get('trailingPE', 'N/A'), period)
exibir_dados("Dividend Yield", lambda period: info.get('dividendYield', 'N/A'), period)
exibir_dados("ROE (Return on Equity)", lambda period: info.get('returnOnEquity', 'N/A'), period)
exibir_dados("P/VP (Preço/Valor Patrimonial)", lambda period: info.get('priceToBook', 'N/A'), period)
exibir_dados("Margem Bruta", lambda period: info.get('grossMargins', 'N/A'), period)
# Adicione outros indicadores fundamentalistas conforme necessário
exibir_dados("Ativo Total", lambda period: acao_escolhida.balance_sheet[0].get('totalAssets', 'N/A'), period)
exibir_dados("Passivo Total", lambda period: acao_escolhida.balance_sheet[0].get('totalLiabilities', 'N/A'), period)
# Adicione outros itens do balanço patrimonial conforme necessário
# Você pode acessar diretamente os dados da demonstração de resultados usando o método 'financials'
exibir_dados("Receita Total", lambda period: acao_escolhida.financials[0].get('totalRevenue', 'N/A'), period)
exibir_dados("Lucro Líquido", lambda period: acao_escolhida.financials[0].get('netIncome', 'N/A'), period)
# Adicione outros itens da demonstração de resultados conforme necessário
# Você pode acessar diretamente os dados do fluxo de caixa usando o método 'cashflow'
exibir_dados("Fluxo de Caixa Operacional", lambda period: acao_escolhida.cashflow[0].get('totalCashFromOperatingActivities', 'N/A'), period)
exibir_dados("Fluxo de Caixa de Investimento", lambda period: acao_escolhida.cashflow[0].get('totalCashflowsFromInvestingActivities', 'N/A'), period)
# Adicione outros itens do fluxo de caixa conforme necessário






#para graficos
exibir_dados("Média Móvel Simples (SMA)", lambda period: acao_escolhida.history(period="max").rolling(window=50).mean(), period)
exibir_dados("Banda de Bollinger", lambda period: acao_escolhida.history(period="max"), period)  # A banda de Bollinger pode ser calculada separadamente
exibir_dados("MACD", lambda period: acao_escolhida.history(period="max"), period)
exibir_dados("RSI", lambda period: acao_escolhida.history(period="max"), period)



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
