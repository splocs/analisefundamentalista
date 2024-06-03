import streamlit as st
import pandas as pd
import yfinance as yf
from PIL import Image
from datetime import date

# Configurando a largura da página
st.set_page_config(layout="wide", page_title="Análise de Ações", page_icon=":chart_with_upwards_trend:")

# Função para formatar a data
def formatar_data(data):
    if data is not None:
        return pd.to_datetime(data, unit='s').strftime('%d-%m-%Y')
    return 'N/A'

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
def pegar_dados_acoes():
    path = 'https://raw.githubusercontent.com/splocs/meu-repositorio/main/acoes.csv'
    return pd.read_csv(path, delimiter=';')

# Função para pegar os valores online
def pegar_valores_online(sigla_acao):
    df = yf.download(sigla_acao, DATA_INICIO, DATA_FIM, progress=False)
    df.reset_index(inplace=True)
    return df

# Função para calcular os indicadores fundamentalistas
def calcular_indicadores(ticker_data):
    indicadores = {}
    try:
        indicadores['P/L'] = ticker_data.info.get('forwardPE', 'N/A')
        indicadores['LPA'] = ticker_data.info.get('trailingEps', 'N/A')
        indicadores['P/VP'] = ticker_data.info.get('priceToBook', 'N/A')
        indicadores['VPA'] = ticker_data.info.get('bookValue', 'N/A')
        indicadores['P/EBIT'] = ticker_data.info.get('enterpriseToEbitda', 'N/A')
        indicadores['Margem Bruta'] = ticker_data.info.get('grossMargins', 'N/A')
        indicadores['Margem EBIT'] = ticker_data.info.get('ebitdaMargins', 'N/A')
        indicadores['Margem Líquida'] = ticker_data.info.get('profitMargins', 'N/A')
        indicadores['ROIC'] = ticker_data.info.get('returnOnAssets', 'N/A')
        indicadores['ROE'] = ticker_data.info.get('returnOnEquity', 'N/A')
    except Exception as e:
        st.error(f"Erro ao calcular os indicadores fundamentalistas: {e}")
    return indicadores

# Função para classificar os indicadores
def classificar_indicador(valor, tipo):
    if valor == 'N/A':
        return 'N/A', 'gray'
    try:
        valor = float(valor)
        if tipo == 'P/L':
            if valor < 15:
                return 'bom', 'green'
            elif valor < 25:
                return 'regular', 'yellow'
            else:
                return 'ruim', 'red'
        elif tipo == 'LPA':
            if valor > 0:
                return 'bom', 'green'
            else:
                return 'ruim', 'red'
        elif tipo == 'P/VP':
            if valor < 1:
                return 'bom', 'green'
            elif valor < 2:
                return 'regular', 'yellow'
            else:
                return 'ruim', 'red'
        elif tipo == 'P/EBIT':
            if valor < 10:
                return 'bom', 'green'
            elif valor < 15:
                return 'regular', 'yellow'
            else:
                return 'ruim', 'red'
        elif tipo == 'Margem Bruta' or tipo == 'Margem EBIT' or tipo == 'Margem Líquida':
            if valor > 0.2:
                return 'bom', 'green'
            elif valor > 0.1:
                return 'regular', 'yellow'
            else:
                return 'ruim', 'red'
        elif tipo == 'ROIC':
            if valor > 0.1:
                return 'bom', 'green'
            elif valor > 0.05:
                return 'regular', 'yellow'
            else:
                return 'ruim', 'red'
        elif tipo == 'ROE':
            if valor > 0.15:
                return 'bom', 'green'
            elif valor > 0.1:
                return 'regular', 'yellow'
            else:
                return 'ruim', 'red'
    except ValueError:
        return 'N/A', 'gray'
    return 'N/A', 'gray'

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

st.title('Análise de Ações')

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

# Coletando os dados fundamentais
ticker_data = yf.Ticker(sigla_acao_escolhida)

<<<<<<< HEAD
=======
# Exibindo informações gerais sobre a empresa
st.subheader('Informações Gerais')
st.write(f"**Papel:** {sigla_acao_escolhida}")
st.write(f"**Cotação:** {ticker_data.info.get('currentPrice', 'N/A')}")
st.write(f"**Tipo:** {ticker_data.info.get('quoteType', 'N/A')}")
st.write(f"**Data da última cotação:** {formatar_data(ticker_data.info.get('regularMarketTime', None))}")
st.write(f"**Empresa:** {ticker_data.info.get('longName', 'N/A')}")
st.write(f"**Setor:** {ticker_data.info.get('sector', 'N/A')}")
st.write(f"**Subsetor:** {ticker_data.info.get('industry', 'N/A')}")
st.write(f"**Valor de mercado:** {ticker_data.info.get('marketCap', 'N/A')}")
st.write(f"**Valor da firma:** {ticker_data.info.get('enterpriseValue', 'N/A')}")
st.write(f"**Número de Ações:** {ticker_data.info.get('sharesOutstanding', 'N/A')}")

# Exibindo as oscilações
st.subheader('Oscilações')
st.write(f"**Oscilação 1 mês:** {ticker_data.info.get('52WeekChange', 'N/A')}")
st.write(f"**Oscilação 6 meses:** {ticker_data.info.get('beta', 'N/A')}")
st.write(f"**Oscilação 1 ano:** {ticker_data.info.get('52WeekHigh', 'N/A')}")

# Calculando e exibindo os indicadores fundamentalistas
st.subheader('Indicadores Fundamentalistas')

# Explicações dos indicadores
explicacoes = {
    'P/L': 'Preço/Lucro: Relação entre o preço da ação e o lucro por ação. Um P/L baixo pode indicar que a ação está subvalorizada.',
    'LPA': 'Lucro por Ação: Lucro líquido da empresa dividido pelo número total de ações.',
    'P/VP': 'Preço/Valor Patrimonial: Relação entre o preço da ação e o valor patrimonial por ação. Um P/VP abaixo de 1 pode indicar que a ação está subvalorizada.',
    'VPA': 'Valor Patrimonial por Ação: Patrimônio líquido da empresa dividido pelo número total de ações.',
    'P/EBIT': 'Preço/Lucro antes dos Juros e Impostos: Relação entre o preço da ação e o lucro antes dos juros e impostos.',
    'Margem Bruta': 'Margem Bruta: Percentual do lucro bruto em relação à receita total. Margens mais altas indicam maior eficiência.',
    'Margem EBIT': 'Margem EBIT: Percentual do lucro antes dos juros e impostos em relação à receita total.',
    'Margem Líquida': 'Margem Líquida: Percentual do lucro líquido em relação à receita total.',
    'ROIC': 'Retorno sobre o Capital Investido: Eficiência da empresa em gerar retorno sobre o capital investido.',
    'ROE': 'Retorno sobre o Patrimônio Líquido: Eficiência da empresa em gerar retorno sobre o patrimônio líquido.'
}

indicadores = calcular_indicadores(ticker_data)
for indicador, valor in indicadores.items():
    classificacao, cor = classificar_indicador(valor, indicador)
    st.write(f"**{indicador}:** {valor} ({classificacao})", unsafe_allow_html=True)
    st.markdown(f"<span style='color:{cor}'>{explicacoes[indicador]}</span>", unsafe_allow_html=True)

# Exibindo dados do Balanço Patrimonial
st.subheader('Dados do Balanço Patrimonial')
balance_sheet = ticker_data.balance_sheet
if not balance_sheet.empty:
    st.write(f"**Ativo:** {balance_sheet.iloc[0].sum()}")
    st.write(f"**Disponibilidades:** {balance_sheet.get('Cash', 'N/A')}")
    st.write(f"**Ativo Circulante:** {balance_sheet.get('Current Assets', 'N/A')}")
    st.write(f"**Dívida Bruta:** {balance_sheet.get('Total Debt', 'N/A')}")
    st.write(f"**Dívida Líquida:** {balance_sheet.get('Net Debt', 'N/A')}")
    st.write(f"**Patrimônio Líquido:** {balance_sheet.get('Total Equity', 'N/A')}")
else:
    st.write('Dados do balanço patrimonial não disponíveis.')

# Exibindo dados dos Demonstrativos de Resultados
st.subheader('Dados dos Demonstrativos de Resultados')
financials = ticker_data.financials
if not financials.empty:
    st.write(f"**Receita Líquida:** {financials.get('Total Revenue', 'N/A')}")
    st.write(f"**EBIT:** {financials.get('Ebit', 'N/A')}")
    st.write(f"**Lucro Líquido:** {financials.get('Net Income', 'N/A')}")
else:
    st.write('Dados dos demonstrativos de resultados não disponíveis.')

# Rodapé
st.markdown("---")
st.write("Desenvolvido por [Seu Nome](https://github.com/seu-usuario)")




>>>>>>> 62d4334f1e7b8660d973a7fda04bff3be1944d6a